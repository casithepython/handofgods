from asyncio import TimeoutError

async def user_react_on_message(bot, ctx, text, wait_user, reactions):
    message = await ctx.send(text)
    for reaction in reactions.keys():
        await message.add_reaction(reaction)

    def check(reaction, user):
        if str(reaction.emoji) not in reactions:
            return False
        if user.id != wait_user.id:
            return False
        if reaction.message.id != message.id:
            return False
        return True

    try:
        user_reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except TimeoutError:
        for reaction in reactions.keys():
            await message.remove_reaction(reaction, ctx.me)
        return None
    emoji = str(user_reaction.emoji)
    for reaction in reactions.keys():
        if reaction != emoji:
            await message.remove_reaction(reaction, ctx.me)
    return reactions[emoji]
