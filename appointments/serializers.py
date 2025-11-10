from rest_framework import serializers
from .models import Specialty, Provider, Availability, Appointment


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name']


class ProviderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    
    class Meta:
        model = Provider
        fields = ['id', 'user', 'user_name', 'specialty', 'specialty_name', 'location']


class AvailabilitySerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.__str__', read_only=True)
    
    class Meta:
        model = Availability
        fields = ['id', 'provider', 'provider_name', 'start', 'end']


class AppointmentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    provider_display = serializers.CharField(source='provider.__str__', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'patient_username', 'patient_name', 
                  'provider', 'provider_display', 'provider_name', 'service',
                  'start', 'end', 'status', 'status_display', 'notes',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        """Auto-populate display names when creating appointment"""
        appointment = super().create(validated_data)
        
        # Auto-fill patient_name if not provided
        if not appointment.patient_name:
            appointment.patient_name = appointment.patient.get_full_name() or appointment.patient.username
        
        # Auto-fill provider_name if not provided
        if not appointment.provider_name:
            appointment.provider_name = str(appointment.provider)
        
        appointment.save()
        return appointment