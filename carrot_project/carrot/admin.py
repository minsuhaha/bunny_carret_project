from django.contrib import admin
from .models import Product, UserProfile, Category, ChatRoom, Message, ChatbotRoom, ChatbotMessage, Review

admin.site.register(Product)
admin.site.register(UserProfile)
admin.site.register(Category)

admin.site.register(ChatRoom)
admin.site.register(Message)

admin.site.register(ChatbotRoom)
admin.site.register(ChatbotMessage)

admin.site.register(Review)
