general-chat = Общий чат

help-text = { $message_text ->
    [start] Привет! Я новогодний Бот Мороз 🎅, помогу вам погрузиться в праздничный вайбик ✨ 
    *[other] 🎄 <b>Я новогодний Бот Мороз для яндексоидов</b>
    }

    Новостной канал бота - <a href="{ $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK }">{ $TELEGRAM_CHANNEL_BOT_NEWS_NAME }</a>

    Баг, фичреквест или что-то ещё - заполняй <a href="{ $YANDEX_FORM_FEEDBACK_LINK }">форму</a>

    <b>🎲 Игры</b>

    <blockquote>❄️ <b>Снежный денёк</b> /snow</blockquote>
    <i>Отправь команду /snow в ответ на сообщение того, в кого хочешь бросить снежок</i>

    <blockquote>❄️🔫 <b>Снежная дуэль</b> /snow_duel</blockquote>
    <i>1️⃣ Расстояние между оппонентами определяется случайно (от 25 до 45 шагов), чем больше расстояние, тем меньше шансов на попадание
    2️⃣ Право первого выстрела определяется в случайном порядке 50/50
    3️⃣ Чем больше дуэлей сыграно, тем больше опыта. Это увеличивает твой шанс попадения в противника. (Текущий бонус можно посмотреть в /stats)
    4️⃣ Игра длится до 2-х попаданий</i>

    <blockquote>☃️ <b>Снеговичок</b> /snowman</blockquote>
    <i>Цель игры слепить самого высокого снеговика. Но будьте аккуратны, он может упасть</i>

    <blockquote>🔮 <b>Предсказания</b> /prediction</blockquote>
    <i>Можно использовать 1 раз в 12ч (ты можешь написать свое предсказание через <a href="{ $YANDEX_FORM_FEEDBACK_LINK_WITH_PRE_COMPLETION }">форму</a>, оно случайно выпадет кому-то)</i>

    { $private_chat_footer -> 
        [true] ⚠️ В лс отвечаю только на команды /help и /stats

        ✅ Чтобы начать играть, добавь меня в группу
       *[other] {""}
    }

night-king-unavailable = Условия для получения секретной ачивки не выполнены, попробуй позже

night-king-unblocked = 
    Ночной король 👑 разблокирован!

    Ачивка отобразится на Стаффе в течение нескольких минут (в редких случаях - в течение часа)

prediction-error-occurred = Произошла ошибка при получении предсказания 😳. Попробуй получить предсказание позже

prediction-next-use-is-allowed-after = Предсказание 🔮 можно получить 1 раз в { $PREDICTION_TIMEOUT_IN_HOURS }ч. Следующее предсказание будет доступно через { $next_use_is_allowed_after }

prediction-no-suitable = Предсказания для тебя закончились 😳. Попробуй получить предсказание позже

prediction = 
    Предсказание 🔮 для @{ $tg_username }

    { $prediction_text }

quiz = Игра пока недоступна, следи за обновлениями в телеграм канале { $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK }

snowball-in-air = @{ $tg_username } бросил(а) снежок ❄️ в воздух

snowball-in-bot = @{ $tg_username } бросил(а) снежок ❄️ в @{ $bot_tg_username }, но не попал(а)

snowball-at-myself = @{ $tg_username } бросил(а) снежок ❄️ в себя

snowball-throw = @{ $tg_username } бросил(а) снежок ❄️ в @{ $to_tg_username }

snowball-is-secret-box = 
    @{ $tg_username } получил(а) подарок 🎁, в котором { $number_snowballs ->
        [one] оказался { $number_snowballs } снежок
        [few] оказалось { $number_snowballs } снежка
       *[many] оказалось { $number_snowballs } снежков
    } ❄️

snowman-bad-request = 
    Укажи число от 1 до 10, на сколько сантиметров нужно увеличить рост снеговичка ☃️

    Пример: <code>/snowman 8</code>

    Чем больше число, тем выше шанс, что снеговичок ☃️ упадет

snowman-text = @{ $tg_username } увеличил(а) рост снеговичка ☃️ на { $height_increased } см

snowman-fall = { snowman-text }, и он упал 🫠 (шанс падения: { $ths_percentage_falling_chance })

snowman-increased = 
    { snowman-text }

    Текущий рост: { $current_height } см

snow-duel-already-in-duel = Ты уже участвуешь в дуэли, если хочешь отменить её, пропиши команду /cancel_snow_duel

snow-duel-start = @{ $tg_username } предлагает сразиться в снежной дуэли ❄️🔫

snow-duel-not-room-exists = Дуэль уже закончилась или не существует

snow-duel-room-already-has-opponent = Ты не участвуешь в этой дэули

snow-duel-user-is-owner-already-in-room = Ты уже участвуешь в этой дуэли

snow-duel-is-current-user-move = Сейчас не твой бросок

snow-duel-cancelled = Дуэль отменена

snow-duel-check-state = Нельзя выполнить это действие, пока ты участвуешь в дуэли. Если хочешь её отменить, вызови команду /cancel_snow_duel

snow-duel-base-info = 
    Расстояние: { $distance } шагов

    Раундов: { $rounds }

    { $health_points_data }

snow-duel-title = ❄️🔫 Снежная дуэль
snow-duel-title-blockquote = <blockquote>{ snow-duel-title }</blockquote>
snow-duel-finished = <blockquote>{ snow-duel-title } (завершена)</blockquote>
snow-duel-cancelled-2 = <blockquote>{ snow-duel-title } (отменена)</blockquote>

snow-duel-winner = 🏆 @{ $tg_username } - побеждает
snow-duel-cancels = ❌ @{ $tg_username } - отменяет
snow-duel-throws = 🔛 @{ $tg_username } - бросает
snow-duel-away =  🔛 @{ $tg_username } - мимо 💨
snow-duel-hit =  🔛 @{ $tg_username } - попал(а) 🎯

sub-msg = Для участия в новогоднем ивенте ✨ нужно убедиться в твоей яндексоидности, для этого подпишись на канал { $TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK }
sub-alert = Для участия в новогоднем ивенте ✨ нужно подписаться на канал, вызови любую команду, там будет ссылка

form = Форма

add-bot-to-group = Добавить бота в группу

throw-snowball = Бросить снежок ❄️

take-challenge = Принять вызов

subscribe = Подписаться ✅

stats = 
    📊 Статистика @{ $tg_username }

    ❄️ Снежный денек:
    - брошено снежков: { $throw }
    - получено снежков: { $get }

    ❄️🔫 Снежная дуэль:
    - выиграно: { $wins } ({ $wins_percentage })
    - проиграно: { $losses } ({ $losses_percentage })
    - бафф: +{ $buff }

    ☃️ Снеговичок:
    - текущий: { $current } см
    - самый высокий: { $maximum } см
    - попыток слепить: { $all_attempts }

    🔮 Предсказания:
    - получено: { $received }
