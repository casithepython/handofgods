from discord.ext import commands
from discord.ext.commands import Context

from handofgods.helpers import OneWord


class AdminCog(commands.Cog):
    async def cog_check(self, ctx: Context):
        return commands.has_permissions(manage_guild=True)

    @commands.group(invoke_without_command=True)
    async def admin(self, ctx: Context):
        """Various administration functions."""
        await ctx.send_help("admin")

    @admin.group(invoke_without_command=True)
    async def tech(self, ctx: Context):
        """Modify tech info."""
        await ctx.send_help("admin tech")

    @admin.group(invoke_without_command=True)
    async def user(self, ctx: Context):
        """Modify user info."""
        await ctx.send_help("admin user")

    @admin.command()
    async def newturn(self, ctx: Context):
        """Go to next turn."""
        raise NotImplementedError  # @TODO

    @admin.command()
    async def pantheon(self, ctx: Context):
        """Gonna be honest I have no idea what this does. --SIG"""
        raise NotImplementedError  # @TODO

    @admin.command()
    async def kill(self, ctx: Context):
        """HALT_AND_CATCH_FIRE"""
        await ctx.bot.close()

    @tech.command()
    async def create(self, ctx: Context, name: OneWord, cost: int):
        """Create a new tech, specifying the
        prerequisites and bonuses after."""
        # await ctx.reply(repr(name) + " " + str(cost))
        raise NotImplementedError  # @TODO

    @tech.command()
    async def attribute(self, ctx: Context, name: str):
        raise NotImplementedError  # @TODO

    @tech.command(name="delete")
    async def tech_delete(self, ctx: Context, name: str):
        """Delete a technology."""
        raise NotImplementedError  # @TODO

    @user.command(name="delete")
    async def user_delete(self, ctx: Context, name: str):
        """Delete a luser."""
        raise NotImplementedError  # @TODO


def setup(bot):
    bot.add_cog(AdminCog())
