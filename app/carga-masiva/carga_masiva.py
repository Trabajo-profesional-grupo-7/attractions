import json
import random
from datetime import datetime, timedelta

from faker import Faker

positive_comments = [
    "Absolutely fantastic!",
    "A marvel to behold!",
    "A real paradise on earth!",
    "Fantastic place to visit!",
    "So much to see and do!",
    "An experience not to be missed!",
    "Delightful!",
    "A real highlight of the trip!",
    "A paradise for explorers!",
    "So much fun!",
    "A true feast for the senses!",
    "Unparalleled charm!",
    "Truly remarkable!",
    "Exhilarating!",
    "An oasis in the city!",
    "Absolutely wonderful!",
    "One of a kind!",
    "Incredible atmosphere!",
    "A true masterpiece!",
    "A must-see destination!",
    "Captivating!",
    "A true delight for the senses!",
    "Well worth the visit!",
    "An enchanting experience!",
    "A truly magical experience!",
    "A real gem of a place!",
    "A real pleasure!",
    "Wonderful experience!",
    "A must-visit destination!",
    "An experience like no other!",
    "Absolutely outstanding!",
    "A feast for the senses!",
    "A real wonderland!",
    "Absolutely delightful!",
    "A true marvel!",
    "A real treasure trove!",
    "Mesmerizing!",
    "Awe-inspiring!",
    "A paradise for nature lovers!",
    "Absolutely charming!",
    "Simply divine!",
    "Highly recommended!",
    "Great value for money!",
    "Thrilling adventure!",
    "A wonder to behold!",
    "Absolutely amazing!",
    "A real joy to visit!",
    "Absolutely spectacular!",
    "A breath of fresh air!",
    "Exceeded all expectations!",
    "A real gem of a destination!",
    "Perfect day out!",
    "Truly enchanting!",
    "Unforgettable moments!",
    "A true treasure!",
    "A slice of paradise!",
    "Absolutely splendid!",
    "Absolutely incredible!",
    "A feast for the eyes!",
    "A real treasure chest!",
    "Pure joy!",
    "Full of surprises!",
    "A real delight to explore!",
    "A joy to explore!",
    "A real treat for the soul!",
    "A real crowd-pleaser!",
    "A real treat!",
    "Absolutely superb!",
    "An oasis of tranquility!",
    "Beautifully curated!",
    "Exquisite beauty!",
    "An absolute paradise!",
    "A true wonder of the world!",
    "A real delight for the senses!",
    "A real paradise!",
    "A real joy to behold!",
    "A wonderful discovery!",
    "A fantastic way to spend the day!",
    "Unforgettable memories!",
    "A wonderful escape!",
    "Absolutely extraordinary!",
    "Enthralling!",
    "A fantastic place to unwind!",
    "A treasure trove of wonders!",
    "Absolutely enchanting!",
    "A real hidden gem!",
    "A real haven of peace!",
    "A real feast for the eyes!",
    "A real dream!",
    "A real haven!",
    "A real marvel!",
    "A real wonder!",
    "Breathtaking views!",
    "A dream come true!",
    "Incredible variety!",
    "Absolutely fabulous!",
    "Absolutely breathtaking!",
    "A hidden gem!",
    "Absolutely stunning!",
    "An absolute joy!",
    "An absolute delight!",
    "Absolutely mesmerizing!",
    "A true gem!",
    "A fantastic outing!",
    "Simply amazing!",
    "Absolutely magnificent!",
    "An unforgettable experience!",
    "A real delight!",
    "A magical journey!",
    "An absolute must-see!",
    "Absolutely magical!",
    "Charming and delightful!",
    "An unforgettable adventure!",
]

negative_comments = [
    "Very unsatisfactory.",
    "Awful place to visit.",
    "Avoid this attraction like the plague.",
    "Very frustrating experience.",
    "Would not waste my time again.",
    "Disappointing visit.",
    "Avoid like the plague.",
    "Not recommended.",
    "Not worth the hype.",
    "Absolutely regrettable.",
    "A huge waste of time and energy.",
    "Absolutely disgusted.",
    "Not recommended at all.",
    "Absolutely dreadful experience.",
    "Disaster.",
    "Absolutely awful experience.",
    "Not worth a visit.",
    "A complete waste.",
    "Not worth the hassle.",
    "Would not visit again.",
    "Wouldn't even give it one star.",
    "Disappointing and frustrating.",
    "A waste of my energy.",
    "Felt like a rip-off.",
    "Very unpleasant.",
    "Very poor quality.",
    "Very dissatisfied.",
    "A complete joke.",
    "Avoid this place.",
    "Extremely dissatisfied.",
    "Pathetic.",
    "Absolutely terrible experience.",
    "Extremely disappointing.",
    "Would not go back again.",
    "Absolutely awful.",
    "A complete letdown.",
    "Would not waste my time here again.",
    "A complete and utter letdown.",
    "Horrendous.",
    "Would not return.",
    "A total disaster.",
    "Highly disappointing.",
    "Disgusted.",
    "A huge disappointment.",
    "Regrettable visit.",
    "Absolutely appalling experience.",
    "Not worth the visit.",
    "Would not recommend.",
    "Absolutely terrible.",
    "Would not recommend to anyone.",
    "A complete letdown and waste of time.",
    "Unsatisfactory.",
    "Wouldn't wish this experience on anyone.",
    "Nothing special.",
    "Very poorly run.",
    "Avoid this place like the plague.",
    "A waste of my time.",
    "Terrible experience!",
    "Absolutely terrible service.",
    "Very disappointed with my visit.",
    "Total waste of time.",
    "Absolutely abysmal.",
    "A complete rip-off and waste of time.",
    "Absolutely horrible.",
    "Very underwhelming experience.",
    "Stay away from this place.",
    "Not what I expected.",
    "An utter disaster.",
    "Not enjoyable at all.",
    "Would not go back.",
    "No fun at all.",
    "A major disappointment.",
    "Not as advertised.",
    "Not what I expected at all.",
    "Unpleasant experience.",
    "Very disappointing place.",
    "Worst attraction I've ever been to.",
    "Unimpressive.",
    "Not even worth the effort.",
    "Wouldn't recommend to my worst enemy.",
    "Hugely disappointing.",
    "Absolutely horrendous.",
    "Very unpleasant experience.",
    "Extremely disappointed.",
    "Absolutely dreadful.",
    "Overrated attraction.",
    "A nightmare.",
    "Avoid this attraction.",
    "Disgusting.",
    "Disgraceful.",
    "Absolutely disgusting.",
    "Worst experience ever.",
    "A terrible experience all around.",
    "Wouldn't recommend to anyone.",
    "A complete waste of my time.",
    "Poorly managed.",
    "Unsatisfactory experience.",
    "Not impressed.",
    "Horrific.",
    "Absolutely appalling service.",
    "Very underwhelming.",
    "An absolute disgrace.",
    "Complete letdown.",
    "A total disappointment.",
    "No redeeming qualities.",
    "Absolutely disgraceful.",
    "Absolutely appalling.",
    "Absolutely unacceptable.",
    "Very frustrating.",
    "Absolutely atrocious.",
    "A complete rip-off.",
    "Unpleasant and disappointing.",
    "Absolutely not worth it.",
    "Wouldn't go if you paid me.",
    "A complete disaster.",
    "Very disappointing.",
    "Dreadful experience.",
    "Horrible experience.",
    "Not worth the effort.",
    "Worst attraction ever.",
    "Avoid at all costs.",
    "Very disappointing visit.",
    "A complete waste of time and money.",
    "Wouldn't waste my time here again.",
    "Extremely unsatisfactory.",
    "Lame attraction.",
    "A big letdown.",
]

types = [
    "amusement_parks",
    "aquariums",
    "art_galleries",
    "bars",
    "beaches",
    "cathedrals",
    "cafes",
    "casinos",
    "historical_landmarks",
    "libraries",
    "museums",
    "national_parks",
    "nightclubs",
    "parks",
    "restaurants",
    "shopping_malls",
    "stadiums",
    "theaters",
    "theme_parks",
    "universities",
]


related_attractions = {
    "amusement_parks": ["theme_parks", "national_parks", "beaches", "casinos"],
    "aquariums": ["museums", "national_parks", "historical_landmarks", "art_galleries"],
    "art_galleries": ["museums", "libraries", "historical_landmarks", "cafes"],
    "bars": ["nightclubs", "restaurants", "cafes", "casinos"],
    "beaches": ["national_parks", "amusement_parks", "theme_parks", "parks"],
    "cathedrals": ["historical_landmarks", "museums", "art_galleries", "libraries"],
    "cafes": ["restaurants", "bars", "shopping_malls", "art_galleries"],
    "casinos": ["nightclubs", "bars", "amusement_parks", "theme_parks"],
    "historical_landmarks": [
        "museums",
        "cathedrals",
        "art_galleries",
        "national_parks",
    ],
    "libraries": ["museums", "art_galleries", "universities", "cathedrals"],
    "museums": ["art_galleries", "historical_landmarks", "libraries", "aquariums"],
    "national_parks": ["beaches", "amusement_parks", "parks", "aquariums"],
    "nightclubs": ["bars", "casinos", "restaurants", "theaters"],
    "parks": ["national_parks", "beaches", "amusement_parks", "theme_parks"],
    "restaurants": ["cafes", "bars", "shopping_malls", "nightclubs"],
    "shopping_malls": ["restaurants", "cafes", "theaters", "amusement_parks"],
    "stadiums": ["theaters", "parks", "casinos", "shopping_malls"],
    "theaters": ["stadiums", "museums", "art_galleries", "nightclubs"],
    "theme_parks": ["amusement_parks", "national_parks", "beaches", "casinos"],
    "universities": ["libraries", "museums", "historical_landmarks", "art_galleries"],
}


attractions = {}

with open("att.txt", "r") as file:
    for line in file:
        line = line.rstrip().split(",")
        attraction_id, type = line[0], line[1]
        attractions_by_type = attractions.get(type, [])
        attractions_by_type.append(attraction_id)
        attractions[type] = attractions_by_type


users = []
n_users = 1000
fake = Faker()
current_time = datetime.now()

for _ in range(0, n_users):
    user = {}
    user["name"] = fake.name()
    first_name, last_name = user["name"].split()[:2]
    user["username"] = f"{first_name.lower()}_{last_name.lower()}"
    user["email"] = f"{first_name.lower()}.{last_name.lower()}@mail.com"
    user["birthday"] = fake.date_of_birth(minimum_age=18, maximum_age=90)

    primary_attraction_type = random.choice([i for i in related_attractions.keys()])
    types_for_user = [primary_attraction_type] + related_attractions[
        primary_attraction_type
    ]

    user["preferences"] = types_for_user

    liked = []
    for _ in range(0, random.randrange(1, 4)):
        liked.append(random.choice(attractions[random.choice(types_for_user)]))
    user["liked"] = liked

    saved = []
    for _ in range(0, random.randrange(1, 4)):
        saved.append(random.choice(attractions[random.choice(types_for_user)]))
    user["saved"] = saved

    done = []
    for _ in range(0, random.randrange(1, 4)):
        done.append(random.choice(attractions[random.choice(types_for_user)]))
    user["done"] = done

    ratings = []
    for _ in range(0, random.randrange(1, 4)):
        ratings.append(
            {
                "attraction_id": random.choice(
                    attractions[random.choice(types_for_user)]
                ),
                "rating": random.randint(4, 5),
            },
        )
    if random.random() > 0.5:
        negative_attraction = random.choice(
            attractions[random.choice(list(set(types).difference(set(types_for_user))))]
        )
        ratings.append(
            {
                "attraction_id": negative_attraction,
                "rating": random.randint(1, 2),
            },
        )
        user["comments"] = [
            {
                "attraction_id": negative_attraction,
                "comment": random.choice(negative_comments),
            }
        ]
    user["ratings"] = ratings

    scheduled = []
    for _ in range(0, random.randrange(1, 4)):
        random_seconds = random.randint(1, 365 * 24 * 60 * 60)
        future_timestamp = current_time + timedelta(seconds=random_seconds)
        scheduled.append(
            {
                "attraction_id": random.choice(
                    attractions[random.choice(types_for_user)]
                ),
                "timestamp": future_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
        )
    user["scheduled"] = scheduled

    attraction_to_comment_positive = random.choice(ratings)["attraction_id"]
    comments = user.get("comments", [])
    comments.append(
        {
            "attraction_id": attraction_to_comment_positive,
            "comment": random.choice(positive_comments),
        }
    )
    user["comments"] = comments

    users.append(user)

with open("users.txt", "w") as file:
    json.dump(users, file, indent=4, default=str)
