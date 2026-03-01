import datetime
import hashlib
import random
from ssl import _Cipher


@bot.command(name="redeem")
async def redeem_product(ctx, code: str):
    """Récupérer un produit acheté"""
    cursor.execute(
        "SELECT product_id FROM transactions WHERE delivery_code = ? AND user_id = ?",
        (code, str(ctx.author.id))
    )
    result = cursor.fetchone()
    
    if not result:
        await ctx.send("❌ Code invalide ou déjà utilisé")
        return
    
    product_id = result[0]
    
    # Générer lien de téléchargement sécurisé
    download_token = hashlib.sha256(f"{code}{datetime.now()}".encode()).hexdigest()[:32]
    download_url = f"https://your-secure-server.com/download/{download_token}"
    
    # Générer mot de passe unique
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Chiffrer les informations
    encrypted_data = _Cipher.encrypt(f"{download_url}|{password}".encode()) # type: ignore
    
    # Envoyer en DM
    embed = discord.Embed(
        title="📦 Livraison du Produit",
        description=f"**Produit:** {PRODUCTS[product_id]['name']}\n\n"
                   f"**Lien de téléchargement (24h):**\n"
                   f"||{download_url}||\n\n"
                   f"**Mot de passe archive:**\n"
                   f"||{password}||\n\n"
                   f"**Instructions:**\n"
                   f"1. Téléchargez l'archive\n"
                   f"2. Décompressez avec le mot de passe ci-dessus\n"
                   f"3. Lisez le README.txt inclus\n\n"
                   f"⚠️ **Supprimez ce message après téléchargement**",
        color=0x3498db
    )
    
    try:
        await ctx.author.send(embed=embed)
        await ctx.send("✅ Produit envoyé en DM. Vérifiez vos messages privés.")
        
        # Marquer comme livré
        cursor.execute(
            "UPDATE transactions SET status = 'DELIVERED' WHERE delivery_code = ?",
            (code,)
        )
        conn.commit()
        
        # Mettre à jour le statut utilisateur
        cursor.execute(
            "UPDATE users SET verified = 1 WHERE discord_id = ?",
            (str(ctx.author.id),)
        )
        
        # Assigner rôle Verified-Buyer
        member = ctx.guild.get_member(ctx.author.id)
        role = discord.utils.get(ctx.guild.roles, name="Verified-Buyer")
        if role and member:
            await member.add_roles(role)
            
    except:
        await ctx.send("❌ Activez vos DMs pour recevoir le produit")
