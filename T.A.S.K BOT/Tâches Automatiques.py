@tasks.loop(minutes=5)
async def check_payments():
    """Vérifier automatiquement les paiements"""
    cursor.execute(
        "SELECT tx_id, user_id, product_id, amount, currency FROM transactions WHERE status = 'PENDING'"
    )
    
    for tx in cursor.fetchall():
        tx_id, user_id, product_id, amount, currency = tx
        
        # Simuler vérification blockchain (à remplacer par API réelle)
        # Ex: API BlockCypher pour BTC, API Monero pour XMR
        payment_confirmed = random.choice([True, False])  # Remplacer par vrai check
        
        if payment_confirmed:
            # Générer code de livraison
            delivery_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            
            cursor.execute(
                "UPDATE transactions SET status = 'COMPLETED', delivery_code = ? WHERE tx_id = ?",
                (delivery_code, tx_id)
            )
            
            # Notifier l'utilisateur
            guild = bot.get_guild(SERVER_ID)
            if guild:
                member = guild.get_member(int(user_id))
                if member:
                    try:
                        embed = discord.Embed(
                            title="✅ Paiement Confirmé",
                            description=f"Votre achat `{product_id}` a été confirmé!\n\n"
                                       f"**Code de livraison:** `{delivery_code}`\n"
                                       f"Utilisez `!redeem {delivery_code}` pour recevoir votre produit",
                            color=0x00ff00
                        )
                        await member.send(embed=embed)
                    except:
                        pass
            
            conn.commit()

@tasks.loop(hours=24)
async def cleanup_old_messages():
    """Nettoyer les anciens messages"""
    guild = bot.get_guild(SERVER_ID)
    
    for channel in guild.text_channels:
        if channel.name in ["orders", "general"]:
            try:
                deleted = await channel.purge(limit=100, check=lambda m: (datetime.now() - m.created_at).days > 7)
                if deleted:
                    print(f"Nettoyé {len(deleted)} messages dans {channel.name}")
            except:
                pass

@bot.event
async def on_ready():
    print(f'{bot.user} connecté!')
    
    # Démarrer les tâches automatiques
    check_payments.start()
    cleanup_old_messages.start()
    
    # Statut personnalisé
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="T.A.S.K Marketplace"
        )
    )

async def check_verification(ctx):
    """Vérifier si l'utilisateur est vérifié"""
    cursor.execute(
        "SELECT verified FROM users WHERE discord_id = ?",
        (str(ctx.author.id),)
    )
    
    result = cursor.fetchone()
    
    if not result or result[0] == 0:
        embed = discord.Embed(
            title="🔒 Accès Restreint",
            description="Vous devez être vérifié pour accéder à cette commande.\n"
                       "Effectuez un premier achat pour obtenir le rôle `Verified-Buyer`.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return False
    
    return True

# Lancer le bot
if __name__ == "__main__":
    bot.run(TOKEN)
