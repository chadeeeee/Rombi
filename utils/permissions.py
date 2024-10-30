from aiogram.types import ChatPermissions

banned = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

free = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True
)

# ADMIN AND USER
ADMIN = {'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True, 'can_delete_messages': True,
         'can_invite_users': True, 'can_restrict_members': True, 'can_pin_messages': True, 'can_promote_members': True}

ADMIN_OWNER = {'is_anonymous': True, 'can_manage_chat': True, 'can_change_info': True, 'can_post_messages': True,
               'can_edit_messages': True, 'can_delete_messages': True,
               'can_invite_users': True, 'can_restrict_members': True, 'can_pin_messages': True,
               'can_manage_video_chats': True, 'can_manage_topics': True}

USER = {'is_anonymous': False, 'can_manage_chat': False, 'can_change_info': False, 'can_post_messages': False,
        'can_edit_messages': False, 'can_delete_messages': False,
        'can_invite_users': True, 'can_restrict_members': False, 'can_pin_messages': False,
        'can_manage_video_chats': False, 'can_manage_topics': False}