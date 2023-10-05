from django.contrib import admin
from .models import Product, UserProfile, Manner, Category, ChatRoom, Message, ChatbotRoom, ChatbotMessage

admin.site.register(Product)
admin.site.register(UserProfile)
admin.site.register(Manner)
admin.site.register(Category)

admin.site.register(ChatRoom)
admin.site.register(Message)

admin.site.register(ChatbotRoom)
admin.site.register(ChatbotMessage)
