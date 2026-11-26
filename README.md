# weidian-catalog

Выгрузка всех товаров магазина 微店 Weidian в CSV/JSON и сайт для их просмотра.

Сайт: **https://tellaboutme.github.io/weidian-catalog/**

## Команда

```sh
./install.sh                  # ставит weidian, weidan и weidian-site в ~/.local/bin

weidian 1350023534            # по userid
weidian "https://shop1350023534.v.weidian.com/?userid=1350023534"
weidian "https://weidian.com/item.html?itemID=4430202158"   # магазин найдётся по товару
weidian 111 222 333 -o ./out  # несколько магазинов, своя папка
```

Файлы сохраняются в `~/weidian/weidian_<id>.csv` и `.json` (папку меняют через `-o` или `$WEIDIAN_DIR`).
CSV в UTF-8 с BOM, поэтому Excel открывает китайский текст без кракозябр.

Колонки: `productId, shopId, createdAt, name, comment, price_cny, sold, stock, hasSku, isPreSale, tags, thumbnail, url`.
Цена указана в юанях. Используется публичный API, который вызывает сам сайт Weidian, ключи не нужны.

## Сайт

Один файл `index.html`, без сборки и зависимостей.

- Перетащите на страницу CSV или JSON (можно несколько сразу) или нажмите «+ CSV / JSON».
- Загруженные магазины хранятся в IndexedDB вашего браузера, на сервер ничего не уходит.
- Поиск, сортировка (продажи, новизна, цена), фильтр по цене, скрытие ссылок-доплат ≤ ¥5, включение и удаление магазинов.
- Понимает и выгрузку Apify `notdemna/weidian-products` (цена там в фэнях, делится на 100).
- Ссылка с данными: `?data=<url>[,<url>]`, например CSV из raw.githubusercontent.com или Gist.

Локально:

```sh
weidian-site                  # http://localhost:8787, файлы из ~/weidian доступны как data/…
```

Скрипт выводит ссылку, которая сразу открывает все выгрузки.
