general-chat = General chat

help-text = { $message_text -> 
    [start] Hello! I'm New Year Bot Moroz 🎅, here to get you into the holiday spirit ✨ 
    *[other] 🎄 <b>I am the New Year Bot Moroz for Yandex users</b>
    }

    Bot's news channel - <a href="{ $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK }">{ $TELEGRAM_CHANNEL_BOT_NEWS_NAME }</a>

    Found a bug, have a feature request, or something else? Fill out <a href="{ $YANDEX_FORM_FEEDBACK_LINK }">the form</a>

    <b>🎲 Games</b>

    <blockquote>❄️ <b>Snowy Day</b> /snow</blockquote>
    <i>Send the /snow command in response to a message from the person you want to throw a snowball at</i>

    <blockquote>❄️🔫 <b>Snow Duel</b> /snow_duel</blockquote>
    <i>1️⃣ The distance between opponents is determined randomly (from 25 to 45 steps); the greater the distance, the lower the hit chance
    2️⃣ The right to shoot first is determined randomly (50/50)
    3️⃣ The more duels played, the more experience gained. This increases your chance of hitting the opponent. (Check your current bonus with /stats)
    4️⃣ The game continues until 2 hits are made</i>

    <blockquote>☃️ <b>Snowman</b> /snowman</blockquote>
    <i>The goal is to build the tallest snowman. Be careful though, it might fall</i>

    <blockquote>🔮 <b>Predictions</b> /prediction</blockquote>
    <i>You can use it once every 12 hours (You can submit your own prediction via <a href="{ $YANDEX_FORM_FEEDBACK_LINK_WITH_PRE_COMPLETION }">the form</a>; it will randomly appear for someone)</i>

    { $private_chat_footer -> 
        [true] ⚠️ In private chat, I only respond to the /help and /stats commands

        ✅ To start playing, add me to a group

        ✅ Or join us in the <a href="{ $TELEGRAM_GROUP_FOR_FLOOD_LINK }">general chat</a>
       *[other] {""}
    }

night-king-unavailable = The conditions for obtaining a secret achievement are not met, try again later

night-king-unblocked = 
    Night King 👑 unlocked!

    The achievement will appear on Staff within a few minutes (in rare cases - within an hour)

prediction-error-occurred = An error occurred while retrieving the prediction 😳. Try again later

prediction-next-use-is-allowed-after = You can receive a prediction 🔮 once every { $PREDICTION_TIMEOUT_IN_HOURS } hours. The next prediction will be available in { $next_use_is_allowed_after }

prediction-no-suitable = No more predictions left for you 😳. Try again later

prediction = 
    Prediction 🔮 for @{ $tg_username }

    { $prediction_text }

quiz = The game is currently unavailable. Follow updates on the Telegram channel { $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK }

snowball-in-air = @{ $tg_username } threw a snowball ❄️ into the air

snowball-in-bot = @{ $tg_username } threw a snowball ❄️ at @{ $bot_tg_username }, but missed

snowball-at-myself = @{ $tg_username } threw a snowball ❄️ at themselves

snowball-throw = @{ $tg_username } threw a snowball ❄️ at @{ $to_tg_username }

snowball-is-secret-box = 
    @{ $tg_username } received a gift 🎁 containing { $number_snowballs ->
        [one] { $number_snowballs } snowball
        [few] { $number_snowballs } snowballs
       *[many] { $number_snowballs } snowballs
    } ❄️

snowman-bad-request = 
    Specify a number from 1 to 10 for how many centimeters to increase the snowman's height ☃️

    Example: <code>/snowman 8</code>

    The larger the number, the higher the chance the snowman ☃️ will fall

snowman-text = @{ $tg_username } increased the snowman's ☃️ height by { $height_increased } cm

snowman-fall = { snowman-text }, and it fell 🫠 (falling chance: { $ths_percentage_falling_chance })

snowman-increased = 
    { snowman-text }

    Current height: { $current_height } cm

snow-duel-already-in-duel = You are already in a duel. If you want to cancel it, use the command /cancel_snow_duel

snow-duel-start = @{ $tg_username } is challenging someone to a snow duel ❄️🔫

snow-duel-not-room-exists = The duel has already ended or does not exist

snow-duel-room-already-has-opponent = You are not participating in this duel

snow-duel-user-is-owner-already-in-room = You are already participating in this duel

snow-duel-is-current-user-move = It is not your turn to throw

snow-duel-cancelled = The duel has been canceled

snow-duel-check-state = You cannot perform this action while in a duel. If you want to cancel it, use the command /cancel_snow_duel

snow-duel-base-info = 
    Distance: { $distance } steps

    Rounds: { $rounds }

    { $health_points_data }

snow-duel-title = ❄️🔫 Snow Duel
snow-duel-title-blockquote = <blockquote>{ snow-duel-title }</blockquote>
snow-duel-finished = <blockquote>{ snow-duel-title } (finished)</blockquote>
snow-duel-cancelled-2 = <blockquote>{ snow-duel-title } (canceled)</blockquote>

snow-duel-winner = 🏆 @{ $tg_username } - wins
snow-duel-cancels = ❌ @{ $tg_username } - cancels
snow-duel-throws = 🔛 @{ $tg_username } - throws
snow-duel-away =  🔛 @{ $tg_username } - misses 💨
snow-duel-hit =  🔛 @{ $tg_username } - hits 🎯

sub-msg = To participate in the New Year's event ✨ you need to subscribe to the channel { $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK }
sub-alert = To participate in the New Year's event ✨ you need to subscribe to the channel, use any command for a link

form = Form

add-bot-to-group = Add the bot to a group

throw-snowball = Throw a snowball ❄️

take-challenge = Accept the challenge

subscribe = Subscribe ✅

stats = 
    📊 Statistics for @{ $tg_username }

    ❄️ Snowy Day:
    - snowballs thrown: { $throw }
    - snowballs received: { $get }

    ❄️🔫 Snow Duel:
    - wins: { $wins } ({ $wins_percentage })
    - losses: { $losses } ({ $losses_percentage })
    - buff: +{ $buff }

    ☃️ Snowman:
    - current height: { $current }
    - tallest height: { $maximum }
    - attempts made: { $all_attempts }

    🔮 Predictions:
    - received: { $received }
