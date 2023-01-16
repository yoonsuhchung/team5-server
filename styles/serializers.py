from rest_framework import serializers

from accounts.models import CustomUser
from styles.models import Follow, Profile


class NestedProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'user_name', 'profile_name', 'img']


class FollowerSerializer(serializers.ModelSerializer):
    from_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['from_profile', 'created_at']
        read_only_fields = ['from_profile', 'created_at']

    def to_representation(self, instance: Follow):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['current_user']
        if current_user.id == instance.from_profile_id:
            return {**representation, 'following': None}

        following = Follow.objects.filter(from_profile=current_user.id,
                                          to_profile=representation.get('from_profile')['user']).exists()
        return {**representation, 'following': following}


class FollowingSerializer(serializers.ModelSerializer):
    to_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['to_profile', 'created_at']
        read_only_fields = ['to_profile', 'created_at']

    def to_representation(self, instance: Follow):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['current_user']
        if current_user.id == instance.to_profile_id:
            return {**representation, 'following': None}

        following = Follow.objects.filter(from_profile=current_user.id,
                                          to_profile=representation.get('to_profile')['user']).exists()
        return {**representation, 'following': following}


class ProfileSerializer(serializers.ModelSerializer):
    num_followers = serializers.SerializerMethodField()
    num_followings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'user_name', 'profile_name', 'introduction', 'img', 'num_followers', 'num_followings']
        read_only_fields = ['user', 'num_followers', 'num_followings']

    def get_num_followers(self, obj: Profile):
        return obj.followers.count()

    def get_num_followings(self, obj: Profile):
        return obj.followings.count()

    def to_representation(self, instance: Profile):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['current_user']
        if current_user.is_anonymous:
            return {**representation, 'following': 'login required'}

        if current_user.id == instance.user_id:
            return {**representation, 'following': None}

        following = Follow.objects.filter(from_profile=current_user.id, to_profile=instance.user_id).exists()
        return {**representation, 'following': following}
