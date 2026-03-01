@bot.command(name="store")
async def show_store(ctx):
    """Afficher les produits disponibles"""
    if not await check_verification(ctx):
        return
    
    embed = discord.Embed(
        title="🛒 T.A.S.K Marketplace",
        description="Outils disponibles à l'achat\n\n"
                   "**Format de commande :**\n"
                   "`!buy [ID] [BTC/XMR]`\n\n"
                   "Ex: `!buy RAT-001 XMR`",
        color=0x7289da
    )
    
    for pid, product in PRODUCTS.items():
        embed.add_field(
            name=f"**{pid}** - {product['name']}",
            value=f"{product['description']}\n"
                  f"💰 **Prix:** {product['price_btc']} BTC | {product['price_xmr']} XMR\n"
                  f"━━━━━━━━━━━━━━━━━━━━",
            inline=False
        )
    
    embed.set_footer(text="Livraison automatique après confirmation blockchain")
    await ctx.send(embed=embed)

@bot.command(name="buy")
async def buy_product(ctx, product_id: str, currency: str = "XMR"):
    """Commander un produit"""
    if not await check_verification(ctx):
        return
    
    if product_id not in PRODUCTS:
        await ctx.send("❌ Produit introuvable. Utilisez `!store`")
        return
    
    if currency not in ["BTC", "XMR"]:
        await ctx.send("❌ Devise invalide. Choisissez BTC ou XMR")
        return
    
    product = PRODUCTS[product_id]
    price = product[f"price_{currency.lower()}"]
    
    # Générer adresse unique
    user_hash = hashlib.sha256(f"{ctx.author.id}{datetime.now()}".encode()).hexdigest()[:16]
    tx_id = f"TX{user_hash.upper()}"
    
    # Générer QR Code
    wallet_address = CRYPTO_WALLETS[currency]
    qr = qrcode.make(f"{currency}:{wallet_address}?amount={price}&label={tx_id}")
    
    # Sauvegarder en mémoire
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    
    # Créer embed de paiement
    embed = discord.Embed(
        title=f"💰 Paiement {currency}",
        description=f"**Produit:** {product['name']}\n"
                   f"**Prix:** {price} {currency}\n"
                   f"**ID Transaction:** `{tx_id}`\n\n"
                   f"Envoyez **exactement** {price} {currency} à :\n"
                   f"```\n{wallet_address}\n```\n"
                   f"**Confirmation automatique après 2 confirmations**\n\n"
                   f"Utilisez `!check {tx_id}` pour vérifier le statut",
        color=0xf1c40f
    )
    
    file = discord.File(buf, filename="payment_qr.png")
    embed.set_image(url="attachment://payment_qr.png")
    
    # Message privé
    try:
        await ctx.author.send(file=file, embed=embed)
        await ctx.send("✅ Instructions de paiement envoyées en DM")
    except:
        await ctx.send("❌ Activez vos DMs pour recevoir les instructions")
    
    # Log transaction
    cursor.execute(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (tx_id, str(ctx.author.id), product_id, price, currency, 
         "PENDING", datetime.now().isoformat(), None)
    )
    conn.commit()

@bot.command(name="check")
async def check_payment(ctx, tx_id: str):
    """Vérifier statut paiement"""
    cursor.execute(
        "SELECT status, delivery_code FROM transactions WHERE tx_id = ? AND user_id = ?",
        (tx_id, str(ctx.author.id))
    )
    result = cursor.fetchone()
    
    if not result:
        await ctx.send("❌ Transaction introuvable")
        return
    
    status, delivery_code = result
    
    if status == "COMPLETED":
        embed = discord.Embed(
            title="✅ Paiement Confirmé",
            description=f"**Code de livraison:** `{delivery_code}`\n\n"
                       f"Utilisez `!redeem {delivery_code}` pour recevoir votre produit",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="⏳ En Attente",
            description=f"Statut: **{status}**\n\n"
                       f"Vérification automatique toutes les 5 minutes",
            color=0xff9900
        )
    
    await ctx.send(embed=embed)
