import main as db
async def tech(bot, ctx, *args):
    if args[0] == "create":
        return await tech_create(bot, ctx, *(args[1:]))
    elif args[0] == "attribute":
        pass
    elif args[0] == "delete":
        pass
    elif args[0] == "newturn":
        return await newturn()
    else:
        await ctx.send('Admin command does not exist')

async def tech_create(bot, ctx, *args):
    async def _get_bonuses():
        bonuses = []
        while True:
            await ctx.send("Enter a bonus in the form <attribute_name> <value>, or \"exit\" to end.")
            bonus = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
            bonus = bonus.content
            if bonus.lower() == "exit":
                break
            else:
                bonus = bonus.split()
                bonuses.append((db.get_attribute_id(bonus[0]),bonus[1]))
        return bonuses
    async def _get_prerequisites():
        prerequisites = []
        while True:
            await ctx.send("Enter a prerequisite in the form <prerequisite_name> <is_hard=true,false> <cost_bonus> or \"exit\" to end.")
            prereq = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
            prereq = prereq.content
            if prereq.lower() == "exit":
                break
            else:
                prereq = prereq.split()
                if prereq[1].lower() in ["true","false"]:
                    prerequisites.append((db.get_tech_id(prereq[0]), prereq[1].lower()=="true",int(prereq[2])))
                else:
                    await ctx.send("Invalid is_hard value.")
        return prerequisites

    name = ' '.join(args[:-1])
    cost = int(args[-1])
    def check_author(author):
        def inner_check(message):
            if message.author.id != ctx.author.id:
                return False
            return True

        return inner_check

    await ctx.send("Please enter the description.")
    description = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
    description = description.content

    bonuses = await _get_bonuses()
    prerequisites = await _get_prerequisites()

    await ctx.send("What should be the cost multiplier for this?")
    multiplier = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
    multiplier = float(multiplier.content)

    output = db.new_tech(name,description,cost,bonuses,prerequisites,multiplier)
    await ctx.send(output[1])

async def newturn():
    return db.new_turn(), str(db.current_turn())

async def user(bot, ctx, *args):
    if args[0] == 'delete':
        return await user_delete(bot, ctx, *(args[1:]))
    else:
        await ctx.send('Admin command does not exist')

async def user_delete(bot, ctx, *args):
    from user_interaction import user_react_on_message
    if len(args) != 0:
        await ctx.send('Invalid command: wrong number of parameters')
        return
    
    user_name = args[0]
    discord_id = db.get_user_by_name(user_name)

    if discord_id is None:
        await ctx.send('User does not exist')
        return

    output_text = 'Are you sure you want to delete the user "{}"?\n :regional_indicator_y: Yes / :regional_indicator_n: No'
    should_delete = await user_react_on_message(bot, ctx, output_text, ctx.author, {
        '\N{REGIONAL INDICATOR SYMBOL LETTER Y}': True,
        '\N{REGIONAL INDICATOR SYMBOL LETTER N}': False
    })

    if should_delete is None:
        await ctx.send('Timed out user deletion')
    elif should_delete:
        await ctx.send('Deleting user')
        db.user_delete(discord_id)
    else:
        await ctx.send('Cancelled user deletion')