import os
import logging
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, ChatMemberHandler, JobQueue, MessageHandler, filters, CommandHandler
# from names_dataset import NameDataset  # Comment out to save memory
from datetime import datetime, timedelta
import json
import pathlib
import threading
from threading import Lock
import asyncio
from mod_messages import MOD_MESSAGES  # Import the mod messages

# Load environment variables
load_dotenv()

# Initialize logging with more detail
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Don't load NameDataset globally - will load only when needed
# nd = NameDataset()

# Channel welcome message
CHANNEL_INFO = """
 *BGMI ELITE MODS का स्वागत है* 🔥

👑 *यहाँ मिलेगा आपको:*
• सबसे OP BGMI Mods और Hacks
• No Ban वाले ESP Hacks
• Pro Players वाले Aimbot
• Premium Features बिल्कुल Free
• Telegram का सबसे बड़ा Mods Collection
• Daily New Updates

💎 *Get Premium Access:*
• Contact @mohit666r या @dexter09011
• Instant Key Delivery
• 24x7 Support
• Special Features

⚡️ *Channel में Active रहो:*
• Instant Mod Updates के लिए
• Special Features पाने के लिए
• VIP Mods का मज़ा लेने के लिए
• Exclusive Downloads पाने के लिए

🎯 *Ab Chicken Dinner Pakka Hai Boss!* 🏆
💪 Ready Ho Jao BGMI में मचाने के लिए! 🚀
"""

# Add server status messages
SERVER_DOWN_MESSAGE = """
🚨 *BGMI MODS SERVER STATUS UPDATE* 🚨

❌ *SERVER CURRENTLY DOWN* ❌

• All Mod Downloads Temporarily Paused
• Technical Team Working on Fix
• Will be Back Soon with Better Features

⏰ *Estimated Recovery Time:* 2-3 Hours

🔔 *Stay Connected:*
• Keep Notifications ON
• We'll Update When Server is Back
• Premium Users Will Get Priority Access

📞 *For Urgent Queries:*
Contact: @mohit666r | @dexter09011

🙏 Thank you for your patience! 🙏
"""

SERVER_UPDATE_MESSAGE = """
🚀 *BGMI MODS SERVER UPDATE* 🚀

⚙️ *SERVER UNDER UPDATE* ⚙️

• Installing New Features
• Upgrading Mod Systems
• Adding Better Protection
• Implementing New Requests

⏰ *Update Duration:* 3-4 Hours

✨ *What's Coming:*
• New ESP Features
• Enhanced Aimbot
• Better Anti-Ban
• More Premium Features

🔔 *Stay Tuned:*
• Major Improvements Coming
• Premium Users Get First Access
• New Version Will Be Worth the Wait!

📞 *For Updates:*
Contact: @mohit666r | @dexter09011

💫 Get Ready for Something Amazing! 💫
"""

SERVER_MAINTENANCE_MESSAGE = """
🛠️ *BGMI MODS MAINTENANCE MODE* 🛠️

⚡️ *SCHEDULED MAINTENANCE* ⚡️

• Regular Security Updates
• Performance Optimization
• System Improvements
• Bug Fixes in Progress

⏰ *Maintenance Duration:* 1-2 Hours

📋 *What We're Doing:*
• Enhancing Mod Stability
• Improving Download Speed
• Updating Security Features
• Fixing Reported Issues

🔔 *Important Notes:*
• Downloads Will Resume Soon
• Premium Users Get Priority
• All Services Will Be Enhanced

📞 *Need Help?*
Contact: @mohit666r | @dexter09011

🌟 Thank You for Your Understanding! 🌟
"""

# Add server status messages
SERVER_FIXED_MESSAGE = """
✅ *BGMI MODS SERVER IS BACK ONLINE!* ✅

🎮 *SERVER STATUS: OPERATIONAL* 🎮

• All Systems Running Smoothly
• All Mod Downloads Restored
• New Features Activated
• Better Performance & Stability

🚀 *What's Working:*
• ESP Hacks - Full Access
• Aimbot Features - Enhanced
• All Premium Features
• Instant Downloads

⚡️ *Premium Users:*
• All Features Active
• Priority Access Restored
• Enhanced Performance
• Zero Ban Risk

📥 *Start Downloading:*
• All Latest Mods Available
• Updated Anti-Ban System
• Improved Stability

📞 *Need Premium Access?*
Contact: @mohit666r | @dexter09011

🎯 *Time to Dominate BGMI Again!* 🏆
"""

ANTICHEAT_MESSAGE = """
⚠️ *BGMI ANTI-CHEAT ALERT* ⚠️

🔍 *HIGH ANTI-CHEAT ACTIVITY DETECTED* 🔍

• Anti-Cheat System is Highly Active
• Increased Ban Reports from Users
• Strict Detection Methods Enabled
• Multiple Accounts Being Flagged

⚡️ *Safety Measures:*
• Avoid Using Old Mods
• Wait for Updated Safe Version
• Don't Use Risky Features
• Keep Backup Accounts Ready

🛡️ *Premium Users:*
• Use Only Latest Updates
• Follow Safety Guidelines
• Keep Mod Settings Low
• Avoid Suspicious Activities

⏰ *Duration:* 24-48 Hours
Stay Low Until Further Notice

📞 *Need Safe Version?*
Contact: @mohit666r | @dexter09011

🔔 *We'll Update When It's Safe!*
"""

TERMS_MESSAGE = """
🎯 *BGMI MODS USAGE TERMS & CONDITIONS* 🎯

📜 *SAFE USAGE GUIDELINES* | *सुरक्षित उपयोग दिशानिर्देश*

*ESP Features* | *ESP सुविधाएं*:
• Bullet Tracking: Max 100m | बुलेट ट्रैकिंग: अधिकतम 100 मीटर
• Player Detection: Max 150m | खिलाड़ी की पहचान: अधिकतम 150 मीटर
• Vehicle ESP: Max 200m | वाहन ESP: अधिकतम 200 मीटर

*Aimbot Settings* | *एमबॉट सेटिंग्स*:
• Close Range: 0-50m | नजदीकी रेंज: 0-50 मीटर
• Mid Range: 50-150m | मध्यम रेंज: 50-150 मीटर
• No Long Range Aimbot | लंबी दूरी का एमबॉट नहीं

*Recoil & Sensitivity* | *रिकॉइल और सेंसिटिविटी*:
• Max Recoil Control: 75% | अधिकतम रिकॉइल कंट्रोल: 75%
• Aim Assist: Medium | एम असिस्ट: मध्यम
• Auto Scope: Off | ऑटो स्कोप: बंद

⚠️ *IMPORTANT WARNINGS* | *महत्वपूर्ण चेतावनियां*:
1. Never exceed these limits | इन सीमाओं को कभी पार न करें
2. Don't use in tournaments | टूर्नामेंट में उपयोग न करें
3. Avoid suspicious movements | संदिग्ध मूवमेंट से बचें
4. Keep settings moderate | सेटिंग्स को मध्यम रखें

🛡️ *SAFETY FIRST* | *सुरक्षा पहले*:
• Use only our official mods | केवल हमारे आधिकारिक मॉड्स का उपयोग करें
• Update regularly | नियमित रूप से अपडेट करें
• Follow all safety guidelines | सभी सुरक्षा दिशानिर्देशों का पालन करें
• Report any issues immediately | किसी भी समस्या की तुरंत रिपोर्ट करें

⚖️ *DISCLAIMER* | *अस्वीकरण*:
We are not responsible for account bans if you exceed these limits or use mods incorrectly.
यदि आप इन सीमाओं को पार करते हैं या मॉड्स का गलत उपयोग करते हैं तो अकाउंट बैन के लिए हम जिम्मेदार नहीं हैं।

📞 *Support & Updates* | *सहायता और अपडेट*:
• @mohit666r
• @dexter09011

Stay Safe, Play Smart! | सुरक्षित रहें, स्मार्ट खेलें! 🎮
"""

SAFE_MESSAGE = """
✅ *BGMI MODS SAFE TO PLAY* ✅

🛡️ *CURRENT STATUS: SAFE* 🛡️

*Anti-Ban Protection:* Active ✓
*Server Status:* Stable ✓
*Detection Risk:* Low ✓
*Ban Reports:* None ✓

🔰 *Safe Features Available:*
• ESP Range: 100m
• Aimbot: Close-Mid Range
• Recoil Control: Enabled
• Vehicle ESP: Active

⚡️ *Premium Features:*
• All Features Working
• No Detection Issues
• Smooth Performance
• Full Protection Active

🎯 *Best Settings for Safe Play:*
• Keep ESP under 150m
• Use Smooth Aimbot
• Avoid Suspicious Moves
• Follow Terms & Conditions

📱 *Device Safety:*
• Anti-Ban: Working
• Bypass: Active
• Protection: Enabled
• Risk Level: Minimal

✨ *Premium Users:*
• All Features Safe to Use
• Enhanced Protection Active
• Priority Support Available
• Instant Updates Access

📞 *Need Premium?*
Contact: @mohit666r | @dexter09011

🎮 Enjoy Safe Gaming! 🎮
"""

# Bot and channel configuration
BOT_USERNAME = 'wrcmodss_bot'
CHANNEL_USERNAME = 'wrcmods'
OWNER_USERNAME = 'mohit666r'  # Channel owner
ADMIN_USERNAME = 'dexter09011'  # Default admin

# Store authorized users (will be updated during runtime)
AUTHORIZED_USERS = set()  # Start with empty set

# Store scheduled announcements
SCHEDULED_ANNOUNCEMENTS = {}

async def check_permission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user has permission to use commands."""
    try:
        user = update.effective_user
        if not user or not user.username:
            logger.error("No valid user found in update")
            return False
            
        username = user.username.lower()  # Convert to lowercase for comparison
        
        # Log the check
        logger.info(f"Checking permissions for @{username}")
        
        # Owner always has access
        if username == OWNER_USERNAME.lower():
            logger.info("✅ Access granted - user is owner")
            return True
            
        # Check if user is in authorized users
        if username.lower() in {u.lower() for u in AUTHORIZED_USERS}:
            logger.info("✅ Access granted - user is authorized")
            return True
            
        logger.info("❌ Access denied - user is not authorized")
        return False
        
    except Exception as e:
        logger.error(f"Error in permission check: {str(e)}")
        return False

async def grant_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Grant bot access to a user. Only owner can use this."""
    try:
        user = update.effective_user
        
        # Only owner can grant access
        if user.username != OWNER_USERNAME:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, only the channel owner can grant bot access."
            )
            return
            
        # Check if username was provided
        if not context.args:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Please provide a username. Example: `/grant_access @username`",
                parse_mode='Markdown'
            )
            return
            
        # Get username to grant access (remove @ if present)
        username = context.args[0].replace('@', '')
        
        # Add to authorized users
        if username in AUTHORIZED_USERS:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"@{username} already has access to the bot."
            )
        else:
            AUTHORIZED_USERS.add(username)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Successfully granted bot access to @{username}"
            )
            logger.info(f"Access granted to {username} by owner")
            
    except Exception as e:
        logger.error(f"Error in grant_access: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error granting access. Please try again."
        )

async def revoke_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Revoke bot access from a user. Only owner can use this."""
    try:
        user = update.effective_user
        
        # Only owner can revoke access
        if user.username != OWNER_USERNAME:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, only the channel owner can revoke bot access."
            )
            return
            
        # Check if username was provided
        if not context.args:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Please provide a username. Example: `/revoke_access @username`",
                parse_mode='Markdown'
            )
            return
            
        # Get username to revoke access (remove @ if present)
        username = context.args[0].replace('@', '')
        
        # Don't allow revoking owner's access
        if username.lower() == OWNER_USERNAME.lower():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Cannot revoke owner's access."
            )
            return
            
        # Remove from authorized users
        if username in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(username)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Successfully revoked bot access from @{username}"
            )
            logger.info(f"Access revoked from {username} by owner")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"@{username} doesn't have bot access."
            )
            
    except Exception as e:
        logger.error(f"Error in revoke_access: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error revoking access. Please try again."
        )

async def list_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all users who have access to the bot."""
    try:
        user = update.effective_user
        
        # Only authorized users can see the list
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you are not authorized to use this command."
            )
            return
            
        # Check if there are any authorized users
        if not AUTHORIZED_USERS:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"""🔑 *Bot Access List*

❌ No users currently have bot access.
Only @{OWNER_USERNAME} can grant access using:
`/grant_access @username`""",
                parse_mode='Markdown'
            )
            return
            
        # Create list of users with access
        users_list = "\n• @".join(sorted(AUTHORIZED_USERS))
        message = f"""🔑 *Bot Access List*

• @{users_list}

*Note:* Only @{OWNER_USERNAME} can grant/revoke access.
Use `/grant_access @username` to give access.
Use `/revoke_access @username` to remove access."""
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode='Markdown'
        )
            
    except Exception as e:
        logger.error(f"Error in list_access: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error listing access. Please try again."
        )

async def send_scheduled_announcement(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a scheduled announcement."""
    try:
        job = context.job
        chat_id = job.data['chat_id']
        message = job.data['message']
        scheduled_by = job.data['scheduled_by']
        
        # Send the announcement without the extra text
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        
        # Remove from stored announcements
        job_id = str(job.id)
        if job_id in SCHEDULED_ANNOUNCEMENTS:
            del SCHEDULED_ANNOUNCEMENTS[job_id]
            
        logger.info(f"Sent scheduled announcement by @{scheduled_by}")
        
    except Exception as e:
        logger.error(f"Error sending scheduled announcement: {str(e)}")

async def schedule_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Schedule an announcement for future time. Format: /schedule HH:MM message"""
    try:
        # Check permission
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, only authorized users can schedule announcements."
            )
            return

        # Check if arguments are provided
        if len(context.args) < 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="""❌ Please provide time and message. Example:
`/schedule 14:30 New ESP Hack Update Coming!`

*Format:*
• Time in 24-hour format (HH:MM)
• Message after the time
• You can use Markdown formatting""",
                parse_mode='Markdown'
            )
            return

        # Get time and message
        time_str = context.args[0]
        message = ' '.join(context.args[1:])
        
        try:
            # Parse time (HH:MM)
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time")
                
            # Get current time and create target time
            now = datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time is in past, schedule for next day
            if target_time < now:
                target_time += timedelta(days=1)
            
            # Calculate delay in seconds
            delay = (target_time - now).total_seconds()
            
            # Schedule the announcement
            job = context.job_queue.run_once(
                send_scheduled_announcement,
                delay,
                data={
                    'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
                    'message': message,
                    'scheduled_by': update.effective_user.username
                }
            )
            
            # Store job in announcements
            job_id = str(job.job.id)
            SCHEDULED_ANNOUNCEMENTS[job_id] = {
                'time': target_time.strftime('%H:%M'),
                'message': message,
                'scheduled_by': update.effective_user.username
            }
            
            # Send confirmation with copyable ID
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"""✅ Announcement scheduled!

⏰ Time: {target_time.strftime('%H:%M')}
📝 Message: {message}
🆔 ID: `{job_id}`

Use `/list_scheduled` to see all scheduled announcements
Use `/cancel_schedule {job_id}` to cancel this announcement""",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Invalid time format. Please use HH:MM (24-hour format)"
            )
            
    except Exception as e:
        logger.error(f"Error in schedule_announcement: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error scheduling announcement. Please try again."
        )

async def list_scheduled(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all scheduled announcements."""
    try:
        # Check permission
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, only authorized users can view scheduled announcements."
            )
            return
            
        if not SCHEDULED_ANNOUNCEMENTS:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📝 No announcements scheduled."
            )
            return
            
        # Create list of announcements
        announcements = []
        for job_id, data in SCHEDULED_ANNOUNCEMENTS.items():
            announcements.append(f"""
*Time:* {data['time']}
*Message:* {data['message']}
*Scheduled by:* @{data['scheduled_by']}
*ID:* `{job_id}`
""")
            
        message = "📅 *Scheduled Announcements:*\n" + "\n---\n".join(announcements)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in list_scheduled: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error listing scheduled announcements. Please try again."
        )

async def cancel_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel a scheduled announcement."""
    try:
        # Check permission
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, only authorized users can cancel announcements."
            )
            return
            
        # Check if job ID is provided
        if not context.args:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="""❌ Please provide the announcement ID to cancel.
Example: `/cancel_schedule 9a165f708a5a42db97d3186ee5e4dc36`""",
                parse_mode='Markdown'
            )
            return
            
        job_id = context.args[0].strip()  # Remove any extra whitespace
        logger.info(f"Attempting to cancel announcement with ID: {job_id}")
        
        # Check if announcement exists
        if job_id not in SCHEDULED_ANNOUNCEMENTS:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="""❌ Announcement not found. Use `/list_scheduled` to see valid IDs.
Make sure to use the complete ID.""",
                parse_mode='Markdown'
            )
            return
            
        # Get announcement details for logging
        announcement = SCHEDULED_ANNOUNCEMENTS[job_id]
        logger.info(f"Found announcement scheduled for {announcement['time']} by @{announcement['scheduled_by']}")
        
        # Remove all jobs with this ID
        removed = False
        for job in context.job_queue.jobs():
            if str(job.id) == job_id:
                job.schedule_removal()
                removed = True
                logger.info(f"Removed job from queue: {job_id}")
                
        if not removed:
            logger.warning(f"No job found in queue with ID: {job_id}")
            
        # Remove from stored announcements
        del SCHEDULED_ANNOUNCEMENTS[job_id]
        logger.info(f"Removed announcement from storage: {job_id}")
        
        # Send success message with plain text to avoid formatting issues
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"""✅ Announcement cancelled successfully!

Cancelled announcement details:
⏰ Time: {announcement['time']}
📝 Message: {announcement['message']}
👤 Scheduled by: @{announcement['scheduled_by']}"""
        )
        
    except Exception as e:
        logger.error(f"Error in cancel_schedule: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error cancelling announcement. Please try again."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands."""
    try:
        # Only show help to authorized users
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you are not authorized to use this bot."
            )
            return
            
        # Different help text for owner vs other users
        if update.effective_user.username == OWNER_USERNAME:
            help_text = """🔧 Available Commands

Server Status Commands
• /server_down - Send server down notification
• /server_update - Send server update notification
• /server_maintenance - Send server maintenance notification
• /server_fixed - Send server back online notification

Alert Commands
• /anticheat - Send anti-cheat warning alert
• /terms - Send mod usage terms & conditions
• /safe - Send safe to play status
• /mod [1-20] - Send mod feature message by number

Announcement Commands
• /schedule - Schedule an announcement (Format: /schedule HH:MM message)
• /list_scheduled - Show all scheduled announcements
• /cancel_schedule - Cancel a scheduled announcement

Access Management Commands
• /grant_access - Give someone access (Format: /grant_access @username)
• /revoke_access - Remove access (Format: /revoke_access @username)
• /list_access - Show all users with bot access
• /help - Show this help message

You are the bot owner - you can grant/revoke access to other users."""
        else:
            help_text = """🔧 Available Commands

Server Status Commands
• /server_down - Send server down notification
• /server_update - Send server update notification
• /server_maintenance - Send server maintenance notification
• /server_fixed - Send server back online notification

Alert Commands
• /anticheat - Send anti-cheat warning alert
• /terms - Send mod usage terms & conditions
• /safe - Send safe to play status
• /mod [1-20] - Send mod feature message by number

Announcement Commands
• /schedule - Schedule an announcement (Format: /schedule HH:MM message)
• /list_scheduled - Show all scheduled announcements
• /cancel_schedule - Cancel a scheduled announcement

Other Commands
• /list_access - Show all users with bot access
• /help - Show this help message

Contact @mohit666r if you need help."""
            
        # Send message without any special formatting
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_text
        )
        logger.info(f"Help message sent to @{update.effective_user.username}")
            
    except Exception as e:
        logger.error(f"Error in help_command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error showing help menu. Please try again."
        )

async def server_down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send server down message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Channel ID not configured"
            )
            return

        user = update.effective_user
        if not user or not user.username:
            logger.error("Invalid user")
            return
            
        username = user.username
        logger.info(f"Server down command from @{username}")

        # Check permission
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ You don't have permission to use this command."
            )
            return

        # Send plain text message first
        message = """🚨 BGMI MODS SERVER STATUS UPDATE 🚨

❌ SERVER CURRENTLY DOWN ❌

• All Mod Downloads Temporarily Paused
• Technical Team Working on Fix
• Will be Back Soon with Better Features

⏰ Estimated Recovery Time: 2-3 Hours

🔔 Stay Connected:
• Keep Notifications ON
• We'll Update When Server is Back
• Premium Users Will Get Priority Access

📞 For Urgent Queries:
Contact: @mohit666r | @dexter09011

🙏 Thank you for your patience!"""

        try:
            # Try sending without any formatting first
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            logger.info(f"✅ Server down message sent by @{username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )

    except Exception as e:
        logger.error(f"Error in server_down: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error occurred. Please try again."
        )

async def server_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send server update message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Channel ID not configured"
            )
            return

        user = update.effective_user
        if not user or not user.username:
            return
            
        username = user.username
        logger.info(f"Server update command from @{username}")

        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ You don't have permission to use this command."
            )
            return

        message = """🚀 BGMI MODS SERVER UPDATE 🚀

⚙️ SERVER UNDER UPDATE ⚙️

• Installing New Features
• Upgrading Mod Systems
• Adding Better Protection
• Implementing New Requests

⏰ Update Duration: 3-4 Hours

✨ What's Coming:
• New ESP Features
• Enhanced Aimbot
• Better Anti-Ban
• More Premium Features

🔔 Stay Tuned:
• Major Improvements Coming
• Premium Users Get First Access
• New Version Will Be Worth the Wait!

📞 For Updates:
Contact: @mohit666r | @dexter09011

💫 Get Ready for Something Amazing! 💫"""

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            logger.info(f"✅ Server update message sent by @{username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )

    except Exception as e:
        logger.error(f"Error in server_update: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error occurred. Please try again."
        )

async def server_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send server maintenance message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found in environment variables")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Error: Channel ID not configured"
            )
            return

        user = update.effective_user
        logger.info(f"Server maintenance command from @{user.username if user else 'unknown'}")

        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you don't have permission to use this command."
            )
            return

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=SERVER_MAINTENANCE_MESSAGE,
                parse_mode='Markdown'
            )
            logger.info(f"Server maintenance message sent to channel by @{user.username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Server maintenance message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in server_maintenance command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

async def server_fixed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send server fixed message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found in environment variables")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Error: Channel ID not configured"
            )
            return

        user = update.effective_user
        logger.info(f"Server fixed command from @{user.username if user else 'unknown'}")

        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you don't have permission to use this command."
            )
            return

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=SERVER_FIXED_MESSAGE,
                parse_mode='Markdown'
            )
            logger.info(f"Server fixed message sent to channel by @{user.username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Server fixed message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in server_fixed command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    # Don't respond to regular messages
    pass

def get_welcome_by_gender(name, username):
    """Get gender-specific welcome message."""
    # Simplified version that doesn't use NameDataset
    # Always use the default male message to save memory
    return (
        f"🎮 *नमस्ते {name}!*\n\n"
        "🔥 *BGMI के सबसे बड़े Mods Channel में आपका स्वागत है!*\n\n"
        "अब आप बनोगे BGMI के Boss! 👑\n"
        "Ready ho jao Lobby में आग लगाने के लिए! 🚀\n\n"
        "🔐 *Premium Key के लिए संपर्क करें:*\n"
        "• @mohit666r\n"
        "• @dexter09011"
    )

async def handle_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle member updates in the chat."""
    
    # Check if this is a new member
    if update.chat_member.new_chat_member.status == "member":
        new_member = update.chat_member.new_chat_member.user
        chat_id = update.chat_member.chat.id
        
        # Get the member's first name
        first_name = new_member.first_name
        username = new_member.username or first_name  # Keep username as backup but don't show it
        
        # Create welcome message using first name
        welcome_message = get_welcome_by_gender(first_name, username)
        
        # Send welcome message and channel info
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_message,
            parse_mode='Markdown'
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=CHANNEL_INFO,
            parse_mode='Markdown'
        )

async def anticheat_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send anti-cheat warning message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found in environment variables")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Error: Channel ID not configured"
            )
            return

        user = update.effective_user
        logger.info(f"Anti-cheat alert command from @{user.username if user else 'unknown'}")

        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you don't have permission to use this command."
            )
            return

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=ANTICHEAT_MESSAGE,
                parse_mode='Markdown'
            )
            logger.info(f"Anti-cheat alert message sent to channel by @{user.username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Anti-cheat alert message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in anticheat_alert command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

async def terms_and_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send terms and conditions message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found in environment variables")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Error: Channel ID not configured"
            )
            return

        user = update.effective_user
        logger.info(f"Terms command from @{user.username if user else 'unknown'}")

        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you don't have permission to use this command."
            )
            return

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=TERMS_MESSAGE,
                parse_mode='Markdown'
            )
            logger.info(f"Terms and conditions message sent to channel by @{user.username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Terms and conditions message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in terms_and_conditions command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

async def safe_to_play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send safe to play message."""
    try:
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found in environment variables")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Error: Channel ID not configured"
            )
            return

        user = update.effective_user
        logger.info(f"Safe play command from @{user.username if user else 'unknown'}")

        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you don't have permission to use this command."
            )
            return

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=SAFE_MESSAGE,
                parse_mode='Markdown'
            )
            logger.info(f"Safe to play message sent to channel by @{user.username}")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Safe to play message sent successfully!"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to send message. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error in safe_to_play command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

async def send_mod_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a mod message based on number."""
    try:
        # Check permission
        if not await check_permission(update, context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, you don't have permission to use this command."
            )
            return

        # Get channel ID
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id:
            logger.error("No channel ID found")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Channel ID not configured"
            )
            return

        # Check if message number was provided
        if not context.args:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="""❌ Please provide a message number (1-20).
Example: `/mod 5` to send message #5

Available messages:
1: ESP Features 
2: Aimbot Features
3: Memory Hacks
4: Skin Features
5: X-Ray Vision
6: Quick-Shoot Features
7: Anti-Ban Protection
8: iCloud Mode
9: Game Enhancements
10: Team Tracking
11: Invisibility
12: Bullet Tracking
13: Vehicle Mods
14: Headshot Master
15: Damage Multiplier
16: Night Vision
17: Drone View
18: Scope Enhancement
19: Speed Boost
20: All-in-One Package""",
                parse_mode='Markdown'
            )
            return

        try:
            # Parse the message number (1-20)
            message_num = int(context.args[0])
            
            # Validate range
            if message_num < 1 or message_num > 20:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Please enter a number between 1 and 20."
                )
                return
                
            # Get message from array (adjusting for 0-based index)
            message_index = message_num - 1
            mod_message = MOD_MESSAGES[message_index]
            
            # Send the message to the channel
            await context.bot.send_message(
                chat_id=chat_id,
                text=mod_message,
                parse_mode='Markdown'
            )
            
            # Confirmation to the user
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Mod message #{message_num} sent successfully!"
            )
            
            logger.info(f"Mod message #{message_num} sent by @{update.effective_user.username}")
            
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Please enter a valid number."
            )
            
    except Exception as e:
        logger.error(f"Error in send_mod_message: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

def main() -> None:
    """Start the bot."""
    # Get the token and chat ID from environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token:
        logger.error("No token found! Make sure to set TELEGRAM_BOT_TOKEN in .env file")
        return

    if not chat_id:
        logger.error("No chat ID found! Make sure to set TELEGRAM_CHAT_ID in .env file")
        return

    # Add default admin to authorized users at startup
    AUTHORIZED_USERS.add(ADMIN_USERNAME)
    logger.info(f"Added default admin @{ADMIN_USERNAME} to authorized users")

    # Create the Application
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("server_down", server_down))
    application.add_handler(CommandHandler("server_update", server_update))
    application.add_handler(CommandHandler("server_maintenance", server_maintenance))
    application.add_handler(CommandHandler("server_fixed", server_fixed))
    application.add_handler(CommandHandler("anticheat", anticheat_alert))
    application.add_handler(CommandHandler("terms", terms_and_conditions))
    application.add_handler(CommandHandler("safe", safe_to_play))
    application.add_handler(CommandHandler("mod", send_mod_message))
    
    # Add scheduling commands
    application.add_handler(CommandHandler("schedule", schedule_announcement))
    application.add_handler(CommandHandler("list_scheduled", list_scheduled))
    application.add_handler(CommandHandler("cancel_schedule", cancel_schedule))
    
    # Add access management commands
    application.add_handler(CommandHandler("grant_access", grant_access))
    application.add_handler(CommandHandler("revoke_access", revoke_access))
    application.add_handler(CommandHandler("list_access", list_access))
    
    logger.info("Added command handlers")

    # Add member update handler
    application.add_handler(ChatMemberHandler(handle_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    # Add message handler last (with filter to ignore commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Added message handlers")

    # Clean start - remove ALL existing jobs
    for job in application.job_queue.jobs():
        job.schedule_removal()
        logger.info(f"Startup: Removed existing job: {job.name}")
    
    # Start the bot
    logger.info(f"Starting bot @{BOT_USERNAME}")
    logger.info(f"Channel: @{CHANNEL_USERNAME}")
    logger.info(f"Channel ID: {chat_id}")
    logger.info(f"Owner: @{OWNER_USERNAME}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()