@bot.event
async def on_member_join(member):
    """Système de vérification automatique"""
    if member.guild.id != SERVER_ID:
        return
    
    # Vérification âge du compte
    account_age = (datetime.now() - member.created_at).days
    if account_age < 30:
        try:
            await member.send(f"❌ Compte trop récent ({account_age} jours). Minimum 30 jours requis.")
            await member.kick(reason="Compte trop récent")
        except:
            pass
        return
    
    # Assigner rôle Membre
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)
    
    # Log dans la DB
    cursor.execute(
        "INSERT OR IGNORE INTO users (discord_id, join_date) VALUES (?, ?)",
        (str(member.id), datetime.now().isoformat())
    )
    conn.commit()
    
    # Message de bienvenue crypté
    welcome_channel = discord.utils.get(member.guild.channels, name="accueil")
    if welcome_channel:
        embed = discord.Embed(
            title="🔒 Nouveau Membre Vérifié",
            description=f"Bienvenue {member.mention} dans **T.A.S.K**\n\n"
                       f"• Lisez les règles dans <#rules>\n"
                       f"• Accédez au store avec `!store`\n"
                       f"• Support via `!ticket`",
            color=0x00ff00
        )
        await welcome_channel.send(embed=embed)
