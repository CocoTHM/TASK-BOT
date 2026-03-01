@bot.command(name="ticket")
async def create_ticket(ctx, *, reason: str = "Support général"):
    """Créer un ticket de support"""
    guild = ctx.guild
    
    # Vérifier si ticket existe déjà
    for channel in guild.channels:
        if channel.name == f"ticket-{ctx.author.name.lower()}":
            await ctx.send("❌ Vous avez déjà un ticket ouvert")
            return
    
    # Créer salon privé
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    
    # Ajouter rôle support
    support_role = discord.utils.get(guild.roles, name="Moderator")
    if support_role:
        overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    channel = await guild.create_text_channel(
        name=f"ticket-{ctx.author.name}",
        overwrites=overwrites,
        category=discord.utils.get(guild.categories, name="SUPPORT")
    )
    
    # Message d'ouverture
    embed = discord.Embed(
        title="🎫 Ticket Ouvert",
        description=f"**Raison:** {reason}\n\n"
                   f"Le staff vous répondra sous peu.\n"
                   f"Utilisez `!close` pour fermer le ticket.",
        color=0x7289da
    )
    
    await channel.send(f"{ctx.author.mention} {support_role.mention if support_role else ''}", embed=embed)
    await ctx.send(f"✅ Ticket créé: {channel.mention}")

@bot.command(name="close")
@commands.has_any_role(*ADMIN_ROLES)
async def close_ticket(ctx):
    """Fermer un ticket"""
    if "ticket-" in ctx.channel.name:
        await ctx.send("🗑️ Fermeture du ticket dans 10 secondes...")
        await asyncio.sleep(10)
        await ctx.channel.delete()
