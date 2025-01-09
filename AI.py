from pyrogram import Client, filters
import re
import imghdr
import config
from pyrogram.types import InputMediaPhoto, InputMediaVideo
import os
import time

api_id = ""
api_hash = ""

source_channel = ['каналы-доноры']
destination_channel = 'бот с ИИ для рерайта текста'
final_channel = 'целевой канал'

app = Client("my_account", api_id=api_id, api_hash=api_hash)

save_media = []
save_photo = None
exceptions = ["реклама", "@", "интеграция", "канал", "и другие слова-исключения"]
except_low = list(map(str.lower, exceptions))
finder = ["слова, после которых текст надо обрезать"]
finder_low = list(map(str.lower, finder))


@app.on_message(filters.chat(source_channel))
def forward_message(client, message):
    link_pattern = re.compile(r'https?://\S+')
    global save_media, save_photo, edit_caption
    try:
        time.sleep(60)
        if message.media_group_id:
            save_media = client.get_media_group(chat_id=message.chat.id, message_id=message.id)
        elif message.photo or message.video:
            save_photo = client.download_media(message)
        elif message.caption:
            lower_caption = message.caption.lower()
            for keyword in finder_low:
                if keyword in lower_caption:
                    print(f'Found keyword: {keyword}')
                    edit_caption = lower_caption.split(keyword)[0].strip()
                    print('Modified Caption:', edit_caption)
                    break
                else:
                    edit_caption = message.caption
            edit_msg = (f"Без лишних фраз от себя и, по возможности, с разделением на абзацы, сделай рерайт "
                        f"текста:\n{edit_caption}")
            if re.search(link_pattern, edit_msg) or any(substring in edit_msg.lower() for substring in except_low):
                print('ссылка или реклама в сообщении')
            else:
                client.send_message(destination_channel, edit_msg)
        else:
            if message.text:
                lower_caption = message.text.lower()
                for keyword in finder_low:
                    if keyword in lower_caption:
                        print(f'Found keyword: {keyword}')
                        edit_caption = lower_caption.split(keyword)[0].strip()
                        print('Modified Caption:', edit_caption)
                        break
                    else:
                        edit_caption = message.text
                edit_msg = (f"без лишних фраз от себя и, по возможности, с разделением на абзацы, сделай "
                            f"рерайт текста:\n{edit_caption}")
                if re.search(link_pattern, edit_msg) or any(substring in edit_msg.lower() for substring in except_low):
                    print('ссылка или реклама в сообщении')
                else:
                    client.send_message(destination_channel, edit_msg)
            else:
                print('что-то здесь не так')
    except Exception as e:
        (print(f"Произошла ошибка: {e}"))


@app.on_message(filters.chat(destination_channel))
def forward_message2(client, message):
    global save_media, save_photo
    try:
        if not message.text.startswith("ChatGPT") and not any(
                substring in message.text.lower() for substring in except_low):
            if save_media and message.text:
                list_media = []
                for i, media in enumerate(save_media):
                    if i == 0:
                        text = message.text
                    else:
                        text = None
                    if hasattr(media, "photo") and media.photo is not None:
                        list_media.append(InputMediaPhoto(media=media.photo.file_id, caption=text))
                    elif hasattr(media, "video") and media.video is not None:
                        list_media.append(InputMediaVideo(media=media.video.file_id, caption=text))
                client.send_media_group(chat_id=final_channel, media=list_media)
            elif save_photo and message.text:
                image_path = save_photo
                image_type = imghdr.what(image_path)
                if image_type:
                    client.send_photo(final_channel, photo=save_photo, caption=message.text)
                else:
                    client.send_video(final_channel, video=save_photo, caption=message.text)
            else:
                client.send_message(final_channel, message.text)
        else:
            print('слова исключения в тексте')
    except Exception as e:
        (print(f"Снова ошибка: {e}"))
    save_media = []
    os.remove(save_photo)


if __name__ == "__main__":
    app.run()