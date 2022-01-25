import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from graphql_jwt.decorators import login_required
from .models import User, Slot, Appointment
from django.utils import timezone


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class SlotType(DjangoObjectType):
    class Meta:
        model = Slot
        fields = "__all__"


class AppointmentType(DjangoObjectType):
    class Meta:
        model = Appointment
        fields = "__all__"


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()


class Query(UserQuery, MeQuery, graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_slots = graphene.List(SlotType)
    all_appointments = graphene.List(AppointmentType)

    get_user = graphene.Field(UserType, username=graphene.String())

    def resolve_get_user(self, info, **kwargs):
        username = kwargs.get('username')

        if username is not None:
            return User.objects.get(username=username)

        return None

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_all_slots(self, info, **kwargs):
        return Slot.objects.all()

    def resolve_all_appointments(self, info, **kwargs):
        return Appointment.objects.all()

# ### Slot CRUD  ###


class SlotInput(graphene.InputObjectType):
    id = graphene.ID()
    slot_interval = graphene.Int()
    start_time = graphene.DateTime()
    created_by = graphene.Int(name="created_by")


class CreateSlot(graphene.Mutation):
    ''' mutation to create slot'''
    class Arguments:
        slot_data = SlotInput(required=True)

    success = graphene.Boolean()
    slot = graphene.Field(SlotType)

    @staticmethod
    @login_required
    def mutate(root, info, slot_data):
        try:
            # get user from info context
            user = info.context.user

            # if slot_interval is not valid, raise error
            if slot_data.get('slot_interval') not in [15, 30, 45]:
                raise Exception("Invalid slot interval. Slot interval must be 15, 30 or 45 minutes")

            # if start_time is not valid, raise error
            if slot_data.get('start_time') < timezone.now():
                raise Exception("Start time is in the past")

            # if a slot for this user and start_time already exists, raise error
            if Slot.objects.filter(created_by=user, start_time=slot_data.get('start_time')).exists():
                raise Exception("Slot already exists")

            slot_instance = Slot(
                slot_interval=slot_data.slot_interval,
                start_time=slot_data.start_time,
                created_by=user)
            slot_instance.save()

            success = True
            return CreateSlot(slot=slot_instance, success=success)
        except Exception as e:
            raise GraphQLError(str(e))


class UpdateSlot(graphene.Mutation):
    ''' mutation to update slot'''
    class Arguments:
        slot_data = SlotInput(required=True)

    success = graphene.Boolean()
    slot = graphene.Field(SlotType)

    @staticmethod
    @login_required
    def mutate(root, info, slot_data):
        try:
            # if slot id does not exist, raise error
            try:
                slot_instance = Slot.objects.get(pk=slot_data.get("id"))
            except Slot.DoesNotExist:
                raise Exception('Slot does not exist')

            # logged in user must match slot created_by
            if info.context.user != slot_instance.created_by:
                raise Exception("You do not have permission to update this slot")
            
            # if slot start_time is in the past, raise error
            if slot_instance.start_time < timezone.now():
                raise Exception("Can not edit. This slot has expired.")

            # if slot is reserved by someone, raise error
            if slot_instance.is_reserved:
                raise Exception("Can not edit. This slot is reserved.")

            # validate updates
            # if slot_interval is not valid, raise error
            if slot_data.get('slot_interval') not in [15, 30, 45]:
                raise Exception("Invalid slot interval")

            # if start_time is not valid, raise error
            if slot_data.get('start_time') < timezone.now():
                raise Exception("Start time is in the past")

            if slot_instance:
                try:
                    slot_instance.slot_interval = slot_data.get("slot_interval")
                    slot_instance.start_time = slot_data.get("start_time")
                    slot_instance.save()
                    print("saved ..... ")
                    success = True
                    return UpdateSlot(slot=Slot.objects.get(pk=slot_instance.id), success=success)
                except Exception as e:
                    print("error ...... ", e)
                    raise Exception(str(e))
        except Exception as e:
            raise GraphQLError(str(e))


class DeleteSlot(graphene.Mutation):
    ''' mutation to delete a slot'''
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()
    slot = graphene.Field(SlotType)

    @staticmethod
    @login_required
    def mutate(root, info, id):

        try:
            # if slot id does not exist, raise error
            try:
                slot_instance = Slot.objects.get(pk=id)
            except Slot.DoesNotExist:
                raise Exception('Slot does not exist')

            # logged in user must match slot created_by
            if info.context.user != slot_instance.created_by:
                raise Exception("You do not have permission to delete this slot")
            
            try:
                slot_instance.delete()
            except Exception as e:
                raise Exception(f"Unable to delete slot. {str(e)}")
            
            return DeleteSlot(slot=slot_instance, success=True)
        except Exception as e:
            raise GraphQLError(str(e))

# ### Appointment CRUD  ###


class AppointmentInput(graphene.InputObjectType):
    id = graphene.ID()
    slot_id = graphene.Int(name="slot")
    client_name = graphene.String()
    client_email = graphene.String()


class CreateAppointment(graphene.Mutation):
    ''' mutation to create appointment'''
    class Arguments:
        appointment_data = AppointmentInput(required=True)

    success = graphene.Boolean()
    appointment = graphene.Field(AppointmentType)

    @staticmethod
    def mutate(root, info, appointment_data):
        try:
            try:
                slot = Slot.objects.get(pk=appointment_data.get('slot_id'))
            except Slot.DoesNotExist:
                raise Exception('Slot does not exist')

            # if slot is reserved, raise error
            if slot.is_reserved:
                raise Exception("Slot is already reserved")

            # get slot's creator
            try:
                slot_creator = User.objects.get(pk=slot.created_by_id)
            except User.DoesNotExist:
                raise Exception('User does not exist')
            
            # if user is inactive, raise error
            if not slot_creator.is_active:
                raise Exception("User is inactive")

            # create appointment
            appointment_instance = Appointment(
                slot=slot,
                client_name=appointment_data.get('client_name'),
                client_email=appointment_data.get('client_email'))
            appointment_instance.save()

            # update slot
            slot.is_reserved = True
            slot.save()

            success = True
            return CreateAppointment(appointment=appointment_instance, success=success)           
        except Exception as e:
            raise GraphQLError(str(e))


class Mutation(AuthMutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()    
    create_slot = CreateSlot.Field()
    update_slot = UpdateSlot.Field()
    delete_slot = DeleteSlot.Field()
    create_appointment = CreateAppointment.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
