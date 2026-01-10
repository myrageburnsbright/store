from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only = True,
        validators = [validate_password]
    )
    confirmation_password = serializers.CharField(
        write_only = True
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'bio', 'password', 
                  'confirmation_password']

    def validate(self, attrs):
        if attrs['confirmation_password'] != attrs['password']:
            raise serializers.ValidationError({
                "password" : "password fields didnt match"
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirmation_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise serializers.ValidationError('User not found.')
        if not user.is_active:
            raise serializers.ValidationError('User is inactive')
        attrs['user'] = user
        return attrs
   

class UserProfileSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'bio', 'created_at', 'updated_at',
            'posts_count', 'comments_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_posts_count(self, obj):
        try:
            return obj.post.count()
        except AttributeError:
            return 0
    
    def get_comments_count(self, obj):
        try:
            return obj.comment.count()
        except AttributeError:
            return 0
        
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'bio')


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, 
                                         validators = [validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'new_password_confirm')
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if user.check_password(value):
            return value
        raise serializers.ValidationError('Password is wrong')
    
    def validate(self, attrs):
        new_password = attrs['new_password']
        new_password_confirm = attrs['new_password_confirm']
        user = self.context['request'].user
        if user.check_password(new_password):
            raise serializers.ValidationError('Password is identical')
    
        if new_password != new_password_confirm:
            raise serializers.ValidationError('passwords should be match!')

        return attrs
    
    def update(self, instance, validated_data):
        new_password = validated_data['new_password']
        instance.set_password(new_password)
        instance.save()
        return instance