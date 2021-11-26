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