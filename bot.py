import os
import discord, aiohttp
import dotenv
from colorama import Back, Fore, Style
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands, ui
from langdetect import detect
import time
import platform
import asyncio
from datetime import datetime, timedelta
import re
import requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

load_dotenv()

bot = commands.Bot(command_prefix="..", intents=discord.Intents.all())

private_key_value = os.environ.get("PRIVATE_KEY").replace("\\n", "\n")
type_value = os.environ.get("TYPE")
project_id_value = os.environ.get("PROJECT_ID")
private_key_id_value = os.environ.get("PRIVATE_KEY_ID")
client_email_value = os.environ.get("CLIENT_EMAIL")
client_id_value = os.environ.get("CLIENT_ID")
auth_uri_value = os.environ.get("AUTH_URI")
token_uri_value = os.environ.get("TOKEN_URI")
auth_provider_x509_cert_url_value = os.environ.get("AUTH_PROVIDER_X509_CERT_URL")
client_x509_cert_url_value = os.environ.get("CLIENT_X509_CERT_URL")
universe_domain_value = os.environ.get("UNIVERSE_DOMAIN")


BOT_TOKEN = os.environ.get("BOT_TOKEN") #Discord Bot token

cred = {
    "type": f"{type_value}",
    "project_id": f"{project_id_value}",
    "private_key_id": f"{private_key_id_value}",
    "private_key": f"{private_key_value}",
    "client_email": f"{client_email_value}",
    "client_id": f"{client_id_value}",
    "auth_uri": f"{auth_uri_value}",
    "token_uri": f"{token_uri_value}",
    "auth_provider_x509_cert_url": f"{auth_provider_x509_cert_url_value}",
    "client_x509_cert_url": f"{client_x509_cert_url_value}",
    "universe_domain": f"{universe_domain_value}",
}


cred = credentials.Certificate(cred)
firebase_admin.initialize_app(
    cred,
    {"databaseURL": "dburl"},   #Change the URL based on your Firebase Realtime DB.
)


@bot.event
async def on_ready():
    prifix = [
        Back.BLACK
        + Fore.BLACK
        + time.strftime("%H:%M:%S IST", time.gmtime())
        + Back.RESET
        + Fore.WHITE
        + Style.BRIGHT
    ]
    print("".join(prifix) + "Logged in as " + Fore.YELLOW + bot.user.name)
    print("".join(prifix) + "Bot ID: " + Fore.YELLOW + str(bot.user.id))
    print("".join(prifix) + "Discord version " + Fore.YELLOW + discord.__version__)
    print("".join(prifix) + "Python version " + Fore.YELLOW + platform.python_version())
    synced = await bot.tree.sync()

    print("Slash Commands Synced " + str(len(synced)) + " commands")


generating_embed = discord.Embed(
    title="Generating Image",
    description="Image Is Generating, It takes 30 ~ 50 seconds to generate",
    color=discord.Color.orange(),
)


async def generate_image(
    prompt, steps, cfg, sampler, negative_prompt, model, timeout=120
):
    counter = 0
    api_url = "https://api.sitius.ir/"
    data = {
        "model": model,
        "prompt": prompt,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler": sampler,
        "negative_prompt": negative_prompt,
    }
    print(data)
    headers = {"auth": "test"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{api_url}v1/generate/", json=data, headers=headers
        ) as response:
            job_id = await response.json()
        while counter < timeout:
            async with session.get(api_url + f"v1/image/{job_id}/") as r:
                if r.status == 200:
                    url = await r.json()
                    return url
                await asyncio.sleep(0.5)
                counter += 0.5


class RetryButton(ui.View):
    def __init__(
        self, prompt, steps, cfg, sampler, negative_prompt, model, user, p1
    ) -> None:
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.steps = steps
        self.cfg = cfg
        self.sampler = sampler
        self.negative_prompt = negative_prompt
        self.user = user
        self.p1 = p1

    @discord.ui.button(
        label="Retry", emoji="♻️", style=discord.ButtonStyle.green, custom_id="retry"
    )
    async def retry(self, interaction: discord.Interaction, button: ui.Button):
        button.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.edit_message(content=None, embed=generating_embed)

        ref = db.reference("/")
        user_id_to_create = f"{interaction.user.id}"
        user_ref = ref.child("users").child(user_id_to_create)
        user_dataindb = user_ref.get()
        credits = user_dataindb.get("credit", 0)
        if credits <= 0:
            return await interaction.edit_original_response(
                content="You Don't have enough Credits. Use Daily Command to Refresh your Credits.",
                embed=None,
            )

        updated_data = {"status": "generating"}
        user_ref.update(updated_data)
        image = await generate_image(
            self.prompt,
            self.steps,
            self.cfg,
            self.sampler,
            self.negative_prompt,
            self.model,
        )

        if image:
            credits = credits - 1
            updated_data = {"status": "idle", "credit": credits}
            user_ref.update(updated_data)
            print(f"Prompt: {self.prompt}\nImage URL: {image}")
            image_embed = discord.Embed(
                title="Generated Image", color=discord.Color.blue()
            )
            image_embed.set_image(url=image)
            image_embed.add_field(name="Prompt", value=self.prompt, inline=False)
            image_embed.add_field(name="Model", value=self.model, inline=False)
            button.disabled = False
            await interaction.message.edit(view=self)
            await interaction.edit_original_response(content=None, embed=image_embed)

        else:
            await interaction.response.edit_message(
                content="Failed to upload image.", embed=None
            )

    async def interaction_check(self, interaction):
        if interaction.user.id != self.p1:
            await interaction.response.send_message(
                f"You do not own this command {interaction.user.mention}",
                ephemeral=True,
            )
        return interaction.user.id == self.p1


async def check_words(prompt: str) -> bool:
    banned_patterns = [
        r"\bloli\b",
        r"\bbaby\b",
        r"\bshota\b",
        r"\bunderage\b",
        r"\bkid\b",
        r"\bchild\b",
        r"\blittle girl\b",
        r"\byoung girl\b",
        r"\bpetite\b",
        r"\blittle boy\b",
        r"\byoung boy\b",
        r"\bteen\b",
        r"\btween\b",
        r"\bminor\b",
        r"\badolescent\b",
        r"\bpreteen\b",
        r"\bsmall girl\b",
        r"\bsmall boy\b",
        # Match age patterns only if the age is below 18
        r"\b(1[0-7]|[1-9])\s?yo\b",  # e.g., 2yo, 15yo (but not 18yo or older)
        r"\b(1[0-7]|[1-9])\s?years?\s?old\b",  # e.g., 3 years old, 10 yrs old (but not 18 or older)
        r"\b(1[0-7]|[1-9])\s?-year-old\b",  # e.g., 4-year-old, 7-year-old (but not 18 or older)
    ]

    prompt_lower = prompt.lower()
    for pattern in banned_patterns:
        if re.search(pattern, prompt_lower):
            return True
    return False


samplers = [
    "Euler",
    "Euler a",
    "LMS",
    "Heun",
    "DPM2",
    "DPM2 a",
    "DPM++ 2S a",
    "DPM++ 2M",
    "DPM++ SDE",
    "DPM fast",
    "DPM adaptive",
    "LMS Karras",
    "DPM2 Karras",
    "DPM2 a Karras",
    "DPM++ 2S a Karras",
    "DPM++ 2M Karras",
    "DPM++ SDE Karras",
    "DDIM",
    "PLMS",
]
models = [
    "3guofeng3_v3.4",
    "absolutereality_v1.8.1",
    "amIReal_v4.1",
    "anything_V5",
    "abyss_orangemix_v3",
    "blazing_drive_v10g",
    "childrensStories_v1_SemiReal",
    "cyberrealistic_v3.3",
    "deliberate_v3",
    "dreamlike_photoreal_v2.0",
    "dreamshaper_v8",
    "edgeOfRealism_eor_v2.0",
    "epicrealism_natural_Sin_RC1",
    "ICantBelieveItsNotPhotography_seco",
    "juggernaut_aftermath",
    "lyriel_v1.6",
    "majicmixRealistic_v4",
    "neverendingDream_v1.22",
    "pastelMixStylizedAnime_pruned",
    "portraitplus_v1.0",
    "Realistic_Vision_v5.0",
    "redshift_diffusion_v1.0",
    "revAnimated_v1.2.2",
    "rundiffusionFX_photorealistic_v1.0",
    "toonyou_beta6",
]


@bot.tree.command(name="diffuse", description="Creates an Art")
@app_commands.guild_only()
@app_commands.choices(
    model=[
        app_commands.Choice(
            name=name.split(" ")[0]
            .rsplit(".", 1)[0]
            .replace("_", " ")
            .replace("-", " ")
            .title(),
            value=name,
        )
        for name in models
    ]
)
@app_commands.choices(sampler=[app_commands.Choice(name=s, value=s) for s in samplers])
async def diffuse(
    interaction: discord.Interaction,
    positive_prompt: str,
    steps: int,
    cfg: int,
    model: app_commands.Choice[str],
    sampler: app_commands.Choice[str],
    negative_prompt: str = None,
):
    await interaction.response.defer()
    ref = db.reference("/")
    user_id_to_create = f"{interaction.user.id}"

    user_ref = ref.child("users").child(user_id_to_create)
    user_dataindb = user_ref.get()
    status = user_dataindb.get("status")
    total_gen = user_dataindb.get("total_generations")
    if status == "generating":
        return await interaction.edit_original_response(
            content="Oops you are already Generating wait until it is Completed",
            embed=None,
        )
    if user_dataindb:
        # User data exists, display it

        print("User data already exists:")
        print(f"User ID: {user_id_to_create}")
        print(f"Total Generations: {user_dataindb.get('total_generations')}")
        print(f"User Name: {user_dataindb.get('user_name')}")
        print(f"Verified for (hours): {user_dataindb.get('last_daily_used')}")
        credits = user_dataindb.get("credit", 0)
        if credits <= 0:
            return await interaction.edit_original_response(
                content="You Don't have enough Credits. Use **</daily:1294374877125415047>** Command to Refresh your Credits.",
                embed=None,
            )
    else:
        # User data doesn't exist, create it
        print(f"User with ID {user_id_to_create} not found. Creating new data...")

        new_user_data = {
            "credit": 25,
            "total_generations": 0,
            "user_name": interaction.user.name,
            "status": "idle",
            "last_daily_used": int(datetime.now().timestamp() * 1000),
        }

        user_ref.set(new_user_data)

        print("New user data created:")
        print(new_user_data)

    prompt = positive_prompt
    if steps > 45:
        steps = 45
    if cfg > 10:
        cfg = 10
    if negative_prompt == None:
        negative_prompt = "canvas frame, cartoon, 3d, ((disfigured)), ((bad art)), ((deformed)), ((extra limbs)), ((close up)), ((b&w)), blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), ((ugly)), (((bad proportions))), (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), (fused fingers), (too many fingers)"
    if await check_words(prompt):
        return await interaction.edit_original_response(
            content="your prompt contain banned word", embed=None
        )
    updated_data = {"status": "generating"}
    user_ref.update(updated_data)
    image = await generate_image(
        prompt, steps, cfg, sampler.value, negative_prompt, model.value
    )

    if image:
        credits = credits - 1
        total_gen = total_gen + 1
        updated_credit = {
            "credit": credits,
            "status": "idle",
            "total_generations": total_gen,
        }
        user_ref.update(updated_credit)
        view = RetryButton(
            prompt,
            steps,
            cfg,
            sampler.value,
            negative_prompt,
            model.value,
            interaction.user.name,
            interaction.user.id,
        )
        print(f"Prompt: {prompt}\nImage URL: {image}")
        image_embed = discord.Embed(title="Generated Image", color=discord.Color.blue())
        image_embed.set_image(url=image)
        image_embed.add_field(name="Prompt", value=prompt, inline=True)
        image_embed.add_field(name="Model", value=model.value, inline=True)
        image_embed.add_field(name="Steps", value=steps, inline=True)
        image_embed.add_field(name="CFG", value=cfg, inline=True)
        image_embed.add_field(name="Sampler", value=sampler.value, inline=True)
        await interaction.edit_original_response(
            content=None, embed=image_embed, view=view
        )

    else:

        await interaction.edit_original_response(
            content="Failed to upload image.", embed=None
        )


@bot.tree.command(name="daily", description="Redeem Daily Credits")
@app_commands.guild_only()
async def daily_command(interaction: discord.Interaction):
    await interaction.response.defer()
    ref = db.reference("/")
    user_id_to_create = f"{interaction.user.id}"
    user_ref = ref.child("users").child(user_id_to_create)
    user_dataindb = user_ref.get()

    if user_dataindb:
        # User data exists, display it
        print("User data already exists:")
        print(f"User ID: {user_id_to_create}")
        print(f"Total Generations: {user_dataindb.get('total_generations')}")
        print(f"User Name: {user_dataindb.get('user_name')}")
        print(f"Verified for (hours): {user_dataindb.get('last_daily_used')}")
        credits = user_dataindb.get("credit", 0)
        last_daily_used_ms = user_dataindb.get("last_daily_used", 0)

        if last_daily_used_ms:
            last_daily_used = datetime.fromtimestamp(last_daily_used_ms / 1000.0)
        else:
            last_daily_used = None

        # Get current time
        current_time = datetime.now()

        # Check if 24 hours have passed since last daily use
        if last_daily_used is None or (current_time - last_daily_used) >= timedelta(
            hours=24
        ):
            # 24 hours passed, add 25 credits
            new_credits = credits + 25
            user_ref.update(
                {
                    "credit": new_credits,
                    "last_daily_used": int(
                        current_time.timestamp() * 1000
                    ),  # Save as milliseconds
                }
            )
            embed = discord.Embed(
                title="Daily Credits Redeemed",
                timestamp=datetime.now(),
                color=discord.Color.green(),
            )
            embed.description = f"25 credits have been added to your account. You now have {new_credits} credits!"
            embed.set_thumbnail(url=interaction.user.display_avatar)
            await interaction.followup.send(embed=embed)

        else:
            # Calculate the remaining time until next daily claim
            next_claim_time = last_daily_used + timedelta(hours=24)
            remaining_time = next_claim_time - current_time
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            embed = discord.Embed(
                title="Daily Credits",
                description=f"You need to wait {hours} hours and {minutes} minutes to claim your next daily credits.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url=interaction.user.display_avatar)
            await interaction.edit_original_response(embed=embed)

    else:
        # User data doesn't exist, create it
        print(f"User with ID {user_id_to_create} not found. Creating new data...")

        new_user_data = {
            "credit": 25,
            "total_generations": 0,
            "user_name": interaction.user.name,
            "status": "idle",
            "last_daily_used": int(datetime.now().timestamp() * 1000),
        }

        user_ref.set(new_user_data)
        embed = discord.Embed(
            title="Welcome!",
            description="You've received 25 daily credits. Enjoy!",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar)
        await interaction.edit_original_response(embed=embed)

        print("New user data created:")
        print(new_user_data)


bot.run("BOT_TOKEN")
