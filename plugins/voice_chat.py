import os
from .utils.utils import modules_help

import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message

from pytgcalls import GroupCall     


group_call = GroupCall(None, path_to_log_file='')

def init_client(func):
    async def wrapper(client, message):
        group_call.client = client
        return await func(client, message)
    return wrapper

@Client.on_message(filters.command('play', ["."]))
async def start_playout(client, message: Message):
    group_call.client = client
    if not message.reply_to_message or not message.reply_to_message.audio:
        await message.edit_text('<b>Reply to a message containing audio</b>')
        return
    input_filename = 'input.raw'
    await message.edit_text('<code>Downloading...</code>')
    audio_original = await message.reply_to_message.download()
    await message.edit_text('<code>Converting..</code>')
    ffmpeg.input(audio_original).output(
        input_filename,
        format='s16le',
        acodec='pcm_s16le',
        ac=2,
        ar='48k'
    ).overwrite_output().run()
    os.remove(audio_original)
    await message.edit_text(f'<code>Playing</code> <b>{message.reply_to_message.audio.title}</b>...')
    group_call.input_filename = input_filename

@Client.on_message(filters.command('volume', ["."]))
@init_client
async def volume(_, message):
    if len(message.command) < 2:
        await message.edit_text('<b>You forgot to pass volume [1-200]</b>')
    await group_call.set_my_volume(message.command[1])
    await message.edit_text(f'<b>Your volume is set to</b><code> {message.command[1]}</code>')

@Client.on_message(filters.command('join', ["."]))
@init_client
async def start(_, message: Message):
    if await group_call.check_group_call():
        await message.edit_text('<b>You are already connected to the voice channel!</b>')
    else:
        await group_call.start(message.chat.id)
        await message.edit_text('<code>Joining successfully!</code>')

@Client.on_message(filters.command('leave_voice', ["."]))
@init_client
async def stop(_, message: Message):
    if await group_call.check_group_call():
        await group_call.stop()
        await message.edit_text('<code>Leaving successfully!</code>')
    else:
        await message.edit_text("<b>You're not in voice chat!</b>")

@Client.on_message(filters.command('stop', ["."]))
@init_client
async def stop_playout(_, message: Message):
    group_call.stop_playout()
    await message.edit_text('<code>Stoping successfully!</code>')

@Client.on_message(filters.command('mute', ["."]))
@init_client
async def mute(_, message: Message):
    group_call.set_is_mute(True)
    await message.edit_text('<code>Sound off!</code>')

@Client.on_message(filters.command('unmute', ["."]))
@init_client
async def unmute(_, message: Message):
    group_call.set_is_mute(False)
    await message.edit_text('<code>Sound on!</code>')

@Client.on_message(filters.command('pause', ["."]))
@init_client
async def pause(_, message: Message):
    group_call.pause_playout()
    await message.edit_text('<code>Paused!</code>')

@Client.on_message(filters.command('resume', ["."]))
@init_client
async def resume(_, message: Message):
    group_call.resume_playout()
    await message.edit_text('<code>Resumed!</code>')


modules_help.update({'voice_chat': '''<b>Help for |voice_chat|\nUsage:</b>
<code>.play</code>
<b>[Reply to a message containing audio]
<code>.volume [1 - 200]</code>
[Set the volume level from 1 to 200]
<code>.join</code>
[Join the voice chat]
<code>.leave_voice</code>
[Leave voice chat]
<code>.stop</code>
[Stop playback]
<code>.mute</code>
[Mute the userbot]
<code>.unmute</code>
[Unmute the userbot]
<code>.pause</code>
[Pause]
<code>.resume</code>
[Resume]</b>''','voice_chat module': '<b>• Voice_chat</b>:<code> play, volume, join, leave_voice, stop, mute, unmute, pause, resume</code>\n'})
