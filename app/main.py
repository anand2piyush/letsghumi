from __future__ import annotations

import hashlib
import hmac
import json
import re
import shutil
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import FastAPI, File, Form, Request, Response, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "site.json"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "letsghumi2026"
COOKIE_NAME = "letsghumi_owner"
COOKIE_SECRET = "letsghumi-local-owner-secret"

TOURISM_TYPES = [
    {
        "id": "weekend",
        "name": "2D1N Weekend",
        "display": "Weekend Trails",
        "tagline": "Quick two-day resets for friends, couples, and families.",
    },
    {
        "id": "devotional",
        "name": "Devotional Tourism",
        "display": "Sacred Yatra",
        "tagline": "Temple routes, rituals, calm stays, and guided local support.",
    },
    {
        "id": "workcation",
        "name": "1 Month Stay",
        "display": "Workcation Residences",
        "tagline": "Long-stay work-from-hills plans for corporate teams and remote employees.",
    },
    {
        "id": "custom",
        "name": "Customise Yourself",
        "display": "Build Your Own Trip",
        "tagline": "Choose your days, pace, route, stay style, and add-ons.",
    },
]

TYPE_LOOKUP = {item["id"]: item for item in TOURISM_TYPES}

app = FastAPI(title="LetsGhumi Tourism")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tour"


def default_data() -> dict[str, Any]:
    return {
        "settings": {
            "brand": "LetsGhumi",
            "whatsapp_url": "https://wa.me/916201086736",
            "instagram_url": "https://instagram.com/divya_viksh",
            "guide_name": "Your Local Guide",
            "guide_image": "",
            "guide_detail": "Friendly route planning, temple timing support, stay coordination, and local food recommendations.",
            "home_instagram_links": [
                "https://www.instagram.com/p/C9demo01/",
                "https://www.instagram.com/p/C9demo02/",
                "https://www.instagram.com/p/C9demo03/",
                "https://www.instagram.com/p/C9demo04/",
            ],
        },
        "cards": [
            {
                "slug": "rishikesh-weekend-river-reset",
                "tourism_type": "weekend",
                "recommended": True,
                "title": "Rishikesh River Reset",
                "card_description": "2D1N rafting, cafes, river walks, and peaceful evening aarti.",
                "price": "6999",
                "discount": "15",
                "detailed_description": "A compact weekend plan with pickup support, riverside stay options, rafting slots, cafe hopping, and a guided Ganga aarti visit. Designed for travellers who want the trip to feel full without becoming tiring.",
                "instagram_links": [
                    "https://www.instagram.com/p/C9demo11/",
                    "https://www.instagram.com/p/C9demo12/",
                ],
                "images": [
                    {
                        "url": "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Morning riverfront views and soft walking routes near the ghats.",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Adventure add-ons can include rafting, short hikes, and cafe trails.",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Evening plans are paced around local food and river aarti timing.",
                    },
                ],
            },
            {
                "slug": "varanasi-sacred-yatra",
                "tourism_type": "devotional",
                "recommended": True,
                "title": "Varanasi Sacred Yatra",
                "card_description": "Temple darshan, Ganga aarti, old-lane walks, and priest coordination.",
                "price": "n/a",
                "discount": "",
                "detailed_description": "A devotional route for travellers who want structure around darshan timings, local transport, rituals, and heritage lanes. Pricing is kept custom because priest services, stay comfort, and group size change the plan.",
                "instagram_links": [
                    "https://www.instagram.com/p/C9demo21/",
                    "https://www.instagram.com/p/C9demo22/",
                ],
                "images": [
                    {
                        "url": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Sunrise boat rides can be added for a calm start before temple visits.",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1627894483216-2138af692e32?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Routes are planned around crowd flow, rituals, and senior-friendly movement.",
                    },
                ],
            },
            {
                "slug": "manali-workcation-residence",
                "tourism_type": "workcation",
                "recommended": True,
                "title": "Manali Workcation Residence",
                "card_description": "Monthly stay with workspace, Wi-Fi, weekend trails, and team add-ons.",
                "price": "34999",
                "discount": "10",
                "detailed_description": "Built for remote employees and small teams who need predictable Wi-Fi, stay support, laundry options, food coordination, and weekend exploration without planning every detail from scratch.",
                "instagram_links": [
                    "https://www.instagram.com/p/C9demo31/",
                    "https://www.instagram.com/p/C9demo32/",
                ],
                "images": [
                    {
                        "url": "https://images.unsplash.com/photo-1605540436563-5bca919ae766?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Long-stay rooms are selected for comfort, light, and reliable daily routines.",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Weekend route options can be added without disturbing workdays.",
                    },
                ],
            },
            {
                "slug": "custom-himalayan-journey",
                "tourism_type": "custom",
                "recommended": True,
                "title": "Custom Himalayan Journey",
                "card_description": "Pick your number of days, stay category, transport, and activities.",
                "price": "n/a",
                "discount": "",
                "detailed_description": "A flexible plan for travellers who already have a rough idea but want local guidance to make it practical. You can decide the number of days, places, transport comfort, food preferences, and activity level.",
                "instagram_links": [
                    "https://www.instagram.com/p/C9demo41/",
                    "https://www.instagram.com/p/C9demo42/",
                ],
                "images": [
                    {
                        "url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Custom plans balance scenic roads, rest time, and local experiences.",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                        "detail": "Routes can be adjusted for families, friends, couples, or solo travellers.",
                    },
                ],
            },
        ],
    }


def load_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_data(default_data())
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    data.setdefault("settings", {})
    data.setdefault("cards", [])
    data["settings"].setdefault("guide_image", "")
    data["settings"].setdefault("home_instagram_links", [])
    for card in data["cards"]:
        card.setdefault("recommended", False)
    return data


def save_data(data: dict[str, Any]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def signed_owner_token() -> str:
    signature = hmac.new(COOKIE_SECRET.encode(), ADMIN_USERNAME.encode(), hashlib.sha256).hexdigest()
    return f"{ADMIN_USERNAME}:{signature}"


def is_owner(request: Request) -> bool:
    return hmac.compare_digest(request.cookies.get(COOKIE_NAME, ""), signed_owner_token())


def owner_required(request: Request) -> Optional[RedirectResponse]:
    if is_owner(request):
        return None
    return RedirectResponse("/owner", status_code=303)


def guide_image_url(settings: dict[str, Any]) -> str:
    if settings.get("guide_image"):
        return settings["guide_image"]
    for name in ("guide.jpeg", "guide.jpg", "guide.png"):
        path = BASE_DIR / "static" / name
        if path.exists():
            return f"/static/{name}"
    return "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=700&q=80"


def whatsapp_message(brand: str, card_title: str = "", tourism_type: str = "") -> str:
    lines = [f"Hi {brand or 'LetsGhumi'}", "I want more details"]
    if card_title:
        details = card_title
        if tourism_type:
            details = f"{details} - {tourism_type}"
        lines.extend(["", details])
    return "\n".join(lines)


def whatsapp_link(base_url: str, brand: str, card_title: str = "", tourism_type: str = "") -> str:
    if not base_url:
        return ""
    base_url = base_url.strip()
    if not base_url:
        return ""

    message = whatsapp_message(brand, card_title, tourism_type)
    if not urlsplit(base_url).scheme:
        digits = re.sub(r"\D+", "", base_url)
        if digits:
            base_url = f"https://wa.me/{digits}"

    parts = urlsplit(base_url)
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "text"]
    query.append(("text", message))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def clean_links(raw_links: list[str], limit: int) -> list[str]:
    return [link.strip() for link in raw_links if link.strip()][:limit]


def price_is_visible(price: Optional[str]) -> bool:
    if not price:
        return False
    return price.strip().lower() not in {"n/a", "na", "not available", "-"}


def discounted_price(price: Optional[str], discount: Optional[str]) -> Optional[str]:
    if not price_is_visible(price):
        return None
    try:
        numeric_price = float(str(price).replace(",", ""))
        numeric_discount = float(discount or 0)
    except ValueError:
        return None
    if numeric_discount <= 0:
        return None
    return f"{round(numeric_price * (100 - numeric_discount) / 100):,}"


templates.env.filters["price_visible"] = price_is_visible
templates.env.filters["discounted_price"] = discounted_price


@app.get("/")
async def home(request: Request):
    data = load_data()
    cards = [card for card in data["cards"] if card.get("recommended")]
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "settings": data["settings"],
            "tourism_types": TOURISM_TYPES,
            "cards": cards,
            "selected_type": "recommended",
            "page_title": "Recommended LetsGhumi plans",
            "page_eyebrow": "Recommended trips",
            "guide_image": guide_image_url(data["settings"]),
            "whatsapp_link": whatsapp_link(data["settings"].get("whatsapp_url", ""), data["settings"].get("brand", "")),
        },
    )


@app.get("/tourism/{slug}")
async def tourism_detail(request: Request, slug: str):
    data = load_data()
    card = next((item for item in data["cards"] if item.get("slug") == slug), None)
    if card is None:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "settings": data["settings"],
            "tourism_types": TOURISM_TYPES,
            "card": card,
            "type_info": TYPE_LOOKUP.get(card.get("tourism_type"), TOURISM_TYPES[-1]),
            "guide_image": guide_image_url(data["settings"]),
            "whatsapp_link": whatsapp_link(
                data["settings"].get("whatsapp_url", ""),
                data["settings"].get("brand", ""),
                card.get("title", ""),
                TYPE_LOOKUP.get(card.get("tourism_type"), TOURISM_TYPES[-1]).get("display", ""),
            ),
        },
    )


@app.get("/owner")
async def owner(request: Request, edit: Optional[str] = None):
    if not is_owner(request):
        return templates.TemplateResponse("owner_login.html", {"request": request, "error": ""})
    data = load_data()
    edit_card = next((item for item in data["cards"] if item.get("slug") == edit), None)
    return templates.TemplateResponse(
        "owner_dashboard.html",
        {
            "request": request,
            "settings": data["settings"],
            "tourism_types": TOURISM_TYPES,
            "cards": data["cards"],
            "edit_card": edit_card,
            "empty_slots": range(6),
            "guide_image": guide_image_url(data["settings"]),
            "whatsapp_link": whatsapp_link(data["settings"].get("whatsapp_url", ""), data["settings"].get("brand", "")),
        },
    )


@app.post("/owner/login")
async def owner_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse("/owner", status_code=303)
        response.set_cookie(COOKIE_NAME, signed_owner_token(), httponly=True, samesite="lax")
        return response
    return templates.TemplateResponse(
        "owner_login.html",
        {"request": request, "error": "Invalid owner credentials."},
        status_code=401,
    )


@app.post("/owner/logout")
async def owner_logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


@app.post("/owner/settings")
async def save_settings(
    request: Request,
    brand: str = Form(...),
    whatsapp_url: str = Form(""),
    instagram_url: str = Form(""),
    guide_name: str = Form(""),
    guide_detail: str = Form(""),
    home_instagram_links: list[str] = Form([]),
    guide_image_file: Optional[UploadFile] = File(None),
):
    redirect = owner_required(request)
    if redirect:
        return redirect
    data = load_data()
    guide_image = store_guide_upload(guide_image_file, data["settings"].get("guide_image", ""))
    data["settings"].update(
        {
            "brand": brand.strip() or "LetsGhumi",
            "whatsapp_url": whatsapp_url.strip(),
            "instagram_url": instagram_url.strip(),
            "guide_name": guide_name.strip(),
            "guide_image": guide_image,
            "guide_detail": guide_detail.strip(),
            "home_instagram_links": clean_links(home_instagram_links, 50),
        }
    )
    save_data(data)
    return RedirectResponse("/owner#settings", status_code=303)


def store_upload(upload: UploadFile, fallback: str, slug: str, index: int) -> str:
    if not upload or not upload.filename:
        return fallback.strip()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename).suffix.lower() or ".jpg"
    safe_name = f"{slug}-{index}{suffix}"
    destination = UPLOAD_DIR / safe_name
    with destination.open("wb") as file:
        shutil.copyfileobj(upload.file, file)
    return f"/static/uploads/{safe_name}"


def store_guide_upload(upload: Optional[UploadFile], fallback: str) -> str:
    if not upload or not upload.filename:
        return fallback.strip()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename).suffix.lower() or ".jpg"
    destination = UPLOAD_DIR / f"guide{suffix}"
    with destination.open("wb") as file:
        shutil.copyfileobj(upload.file, file)
    return f"/static/uploads/guide{suffix}"


@app.post("/owner/cards")
async def save_card(
    request: Request,
    original_slug: str = Form(""),
    title: str = Form(...),
    tourism_type: str = Form(...),
    card_description: str = Form(...),
    price: str = Form(""),
    discount: str = Form(""),
    recommended: Optional[str] = Form(None),
    detailed_description: str = Form(""),
    image_detail: list[str] = Form([]),
    image_url: list[str] = Form([]),
    existing_image: list[str] = Form([]),
    instagram_links: list[str] = Form([]),
    image_file: list[UploadFile] = File([]),
):
    redirect = owner_required(request)
    if redirect:
        return redirect
    data = load_data()
    slug = slugify(title)
    duplicate = any(card.get("slug") == slug and card.get("slug") != original_slug for card in data["cards"])
    if duplicate:
        slug = f"{slug}-{len(data['cards']) + 1}"

    images = []
    for index in range(6):
        url = image_url[index].strip() if index < len(image_url) else ""
        fallback = existing_image[index].strip() if index < len(existing_image) else ""
        detail = image_detail[index].strip() if index < len(image_detail) else ""
        upload = image_file[index] if index < len(image_file) else None
        final_url = store_upload(upload, url or fallback, slug, index + 1)
        if final_url or detail:
            images.append({"url": final_url, "detail": detail})

    card = {
        "slug": slug,
        "tourism_type": tourism_type if tourism_type in TYPE_LOOKUP else "custom",
        "title": title.strip(),
        "card_description": card_description.strip(),
        "price": price.strip(),
        "discount": discount.strip(),
        "recommended": recommended == "on",
        "detailed_description": detailed_description.strip(),
        "images": images[:6],
        "instagram_links": clean_links(instagram_links, 10),
    }

    if original_slug:
        data["cards"] = [card if item.get("slug") == original_slug else item for item in data["cards"]]
    else:
        data["cards"].append(card)
    save_data(data)
    return RedirectResponse("/owner#cards", status_code=303)


@app.post("/owner/cards/{slug}/delete")
async def delete_card(request: Request, slug: str):
    redirect = owner_required(request)
    if redirect:
        return redirect
    data = load_data()
    data["cards"] = [card for card in data["cards"] if card.get("slug") != slug]
    save_data(data)
    return RedirectResponse("/owner#cards", status_code=303)


@app.get("/{tourism_type}")
async def tourism_type_page(request: Request, tourism_type: str):
    if tourism_type not in TYPE_LOOKUP:
        return RedirectResponse("/", status_code=303)
    data = load_data()
    type_info = TYPE_LOOKUP[tourism_type]
    cards = [card for card in data["cards"] if card.get("tourism_type") == tourism_type]
    return templates.TemplateResponse(
        "category.html",
        {
            "request": request,
            "settings": data["settings"],
            "tourism_types": TOURISM_TYPES,
            "cards": cards,
            "selected_type": tourism_type,
            "page_title": f"{type_info['display']} plans",
            "page_eyebrow": type_info["name"],
            "guide_image": guide_image_url(data["settings"]),
            "whatsapp_link": whatsapp_link(data["settings"].get("whatsapp_url", ""), data["settings"].get("brand", "")),
        },
    )
