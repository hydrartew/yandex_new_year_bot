night-king = Ночной король
night-king-symbol = 👑

predictions = Предсказания
prediction-symbol = 🔮

snow-duel = Снежная дуэль
snow-duel-symbol = ❄️🔫

snow = Снежный денёк
snow-symbol = ❄️

snowman = Снеговичок
snowman-symbol = ☃️

help-text = { $message_text -> 
    [start] Привет! Я новогодний Бот Мороз 🎅, помогу вам погрузиться в праздничный вайбик ✨ 
    *[other] 🎄 <b>Я новогодний Бот Мороз для яндексоидов</b>
    }

    Новостной канал бота - <a href="{ $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK }">{ $TELEGRAM_CHANNEL_BOT_NEWS_NAME }</a>

    Баг, фичреквест или что-то ещё - заполняй <a href="{ $YANDEX_FORM_FEEDBACK_LINK }">форму</a>

    <b>🎲 Игры</b>

    <blockquote>{ snow-symbol } <b>{ snow }</b> /snow</blockquote>
    <i>Отправь команду /snow в ответ на сообщение того, в кого хочешь бросить снежок</i>

    <blockquote>{ snow-duel-symbol } <b>{ snow-duel }</b> /snow_duel</blockquote>
    <i>1️⃣ Расстояние между оппонентами определяется случайно (от 25 до 45 шагов), чем больше расстояние, тем меньше шансов на попадание
    2️⃣ Право первого выстрела определяется в случайном порядке 50/50
    3️⃣ Чем больше дуэлей сыграно, тем больше опыта. Это увеличивает твой шанс попадения в противника. (Текущий бонус можно посмотреть в /stats)
    4️⃣ Игра длится до 2-х попаданий</i>

    <blockquote>{ snowman-symbol } <b>{ snowman }</b> /snowman</blockquote>
    <i>Цель игры слепить самого высокого снеговика. Но будьте аккуратны, он может упасть</i>

    <blockquote>{ prediction-symbol } <b>{ predictions }</b>  /prediction</blockquote>
    <i>Можно использовать 1 раз в 12ч (ты можешь написать свое предсказание через <a href="{ $YANDEX_FORM_FEEDBACK_LINK_WITH_PRE_COMPLETION }">форму</a>, оно случайно выпадет кому-то)</i>

    { $private_chat_footer -> 
        [true] ⚠️ В лс отвечаю только на команды /help и /stats

        ✅ Чтобы начать играть, добавь меня в группу
       *[other] {""}
    }

night-king-unavailable = Пока недоступно, попробуй позже

night-king-unblocked = 
    { night-king } { night-king-symbol } разблокирован!

    Ачивка отобразится на Стаффе в течение нескольких минут (в редких случаях - в течение часа)

prediction-error-occurred = Произошла ошибка при получении предсказания 😳. Попробуй получить предсказание позже

prediction-next-use-is-allowed-after = 
    Предсказание { prediction-symbol } можно получить 1 раз в { $PREDICTION_TIMEOUT_IN_HOURS }ч. Следующее предсказание будет доступно через { $next_use_is_allowed_after }

prediction-no-suitable = Предсказания для тебя закончились 😳. Попробуй получить предсказание позже

prediction = 
    Предсказание { prediction-symbol } для @{ $tg_username }

    { $prediction_text }

quiz = 
    Игра пока недоступна, следи за обновлениями в телеграм канале { $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK }

snowball-in-air = @{ $tg_username } бросил(а) снежок ❄️ в воздух

snowball-in-bot = @{ $tg_username } бросил(а) снежок ❄️ в @{ $bot_tg_username }, но не попал(а)

snowball-at-myself = @{ $tg_username } бросил(а) снежок ❄️ в себя

snowball-throw = @{ $tg_username } бросил(а) снежок в @{ $to_tg_username }

snowball-is-secret-box = 
    @{ $tg_username } получил(а) подарок 🎁, в котором { $number_snowballs ->
        [one] оказался { $number_snowballs } снежок
        [few] оказалось { $number_snowballs } снежка
       *[many] оказалось { $number_snowballs } снежков

    } ❄️
