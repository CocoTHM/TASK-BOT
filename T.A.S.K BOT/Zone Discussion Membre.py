@bot.command(name="forum")
async def create_forum(ctx):
    """Créer une zone de discussion forum"""
    if not any(role.name in ADMIN_ROLES for role in ctx.author.roles):
        await ctx.send("❌ Permission refusée")
        return
    
    # Créer catégorie Forum
    category = await ctx.guild.create_category("💬 FORUM MEMBRES")
    
    # Créer salons forum
    forum_channels = [
        ("💻-technical-talk", "Discussions techniques avancées"),
        ("🛡️-opsec-discussion", "Bonnes pratiques OPSEC"),
        ("🔧-tool-dev", "Développement d'outils"),
        ("📚-tutorials", "Tutoriels partagés"),
        ("🎯-bug-reports", "Rapports de bugs")
    ]
    
    for channel_name, topic in forum_channels:
        await ctx.guild.create_text_channel(
            name=channel_name,
            category=category,
            topic=topic
        )
    
    # Salon général forum
    general_forum = await ctx.guild.create_text_channel(
        name="general-forum",
        category=category,
        topic="Discussion générale entre membres vérifiés"
    )
    
    # Configurer les permissions
    verified_role = discord.utils.get(ctx.guild.roles, name="Verified-Buyer")
    member_role = discord.utils.get(ctx.guild.roles, name="Member")
    
    if verified_role and member_role:
        # Verified-Buyer: lecture/écriture complète
        await general_forum.set_permissions(verified_role,
            read_messages=True,
            send_messages=True,
            add_reactions=True,
            attach_files=True
        )
        
        # Member: lecture seule
        await general_forum.set_permissions(member_role,
            read_messages=True,
            send_messages=False,
            add_reactions=False
        )
        
        # @everyone: refusé
        await general_forum.set_permissions(ctx.guild.default_role,
            read_messages=False
        )
    
    embed = discord.Embed(
        title="💬 Forum Membres Créé",
        description=f"**Catégorie:** {category.mention}\n\n"
                   f"**Salons disponibles:**\n"
                   f"• `💻-technical-talk` - Discussions techniques\n"
                   f"• `🛡️-opsec-discussion` - Sécurité opérationnelle\n"
                   f"• `🔧-tool-dev` - Développement\n"
                   f"• `📚-tutorials` - Tutoriels\n"
                   f"• `🎯-bug-reports` - Bugs\n"
                   f"• `general-forum` - Discussion générale\n\n"
                   f"**Accès:** Rôle `Verified-Buyer` requis pour poster",
        color=0x9b59b6
    )
    
    await ctx.send(embed=embed)

@bot.command(name="suggest")
async def suggest_topic(ctx, *, suggestion: str):
    """Suggérer un nouveau sujet de discussion"""
    if not await check_verification(ctx):
        return
    
    # Envoyer dans le salon suggestions
    suggestions_channel = discord.utils.get(ctx.guild.channels, name="💡-suggestions")
    if not suggestions_channel:
        suggestions_channel = await ctx.guild.create_text_channel(
            "💡-suggestions",
            topic="Suggestions pour le forum"
        )
    
    embed = discord.Embed(
        title="💡 Nouvelle Suggestion",
        description=suggestion,
        color=0xe67e22
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    
    message = await suggestions_channel.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    
    await ctx.send("✅ Suggestion envoyée!")
