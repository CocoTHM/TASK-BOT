@bot.command(name="addproduct")
@commands.has_any_role(*ADMIN_ROLES)
async def add_product(ctx, product_id: str, name: str, price_btc: float, price_xmr: float, *, description: str):
    """Ajouter un produit au store"""
    PRODUCTS[product_id] = {
        "name": name,
        "price_btc": price_btc,
        "price_xmr": price_xmr,
        "description": description
    }
    
    cursor.execute(
        "INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (product_id, name, description, price_btc, price_xmr, None, None, -1)
    )
    conn.commit()
    
    await ctx.send(f"✅ Produit `{product_id}` ajouté au store")

@bot.command(name="stats")
@commands.has_any_role(*ADMIN_ROLES)
async def show_stats(ctx):
    """Afficher les statistiques du bot"""
    cursor.execute("SELECT COUNT(*) FROM users WHERE verified = 1")
    verified_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'COMPLETED'")
    completed_sales = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE status = 'COMPLETED' AND currency = 'BTC'")
    total_btc = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE status = 'COMPLETED' AND currency = 'XMR'")
    total_xmr = cursor.fetchone()[0] or 0
    
    embed = discord.Embed(
        title="📊 Statistiques T.A.S.K",
        color=0x2ecc71
    )
    
    embed.add_field(name="👥 Membres Vérifiés", value=str(verified_users), inline=True)
    embed.add_field(name="🛒 Ventes Complétées", value=str(completed_sales), inline=True)
    embed.add_field(name="💰 Total BTC", value=f"{total_btc:.8f} BTC", inline=True)
    embed.add_field(name="💰 Total XMR", value=f"{total_xmr:.2f} XMR", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name="wipe")
@commands.has_any_role(*ADMIN_ROLES)
async def emergency_wipe(ctx):
    """Commande d'urgence - Supprime tous les salons"""
    confirm_msg = await ctx.send("🚨 **ALERTE URGENCE** - Confirmez la suppression complète avec `!confirmwipe`")
    
@bot.command(name="confirmwipe")
@commands.has_any_role(*ADMIN_ROLES)
async def confirm_wipe(ctx):
    """Confirmer la suppression d'urgence"""
    guild = ctx.guild
    
    # Sauvegarder les logs
    backup_data = []
    for channel in guild.text_channels:
        try:
            async for message in channel.history(limit=100):
                backup_data.append(f"{message.created_at} - {message.author}: {message.content}")
        except:
            pass
    
    # Supprimer tous les salons
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.5)
        except:
            pass
    
    # Recréer un salon d'urgence
    emergency_channel = await guild.create_text_channel("🚨-emergency-recovery")
    
    await emergency_channel.send(
        "✅ Serveur nettoyé. Utilisez l'invitation de backup pour restaurer."
    )
