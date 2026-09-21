# Recca's Kitchen 🍲

**Authentic Nigerian Cuisine** — Online ordering website inspired by African Taste ATL.

📍 2948 Sweet Red Circle, Braselton, GA 30517
📞 (857) 318-6247

## 🌐 Live URL
[https://d3apxkmyzymqhd.cloudfront.net](https://d3apxkmyzymqhd.cloudfront.net)

## ✨ Features
- **Online Menu** — 31 items across 6 categories (Starters, Soups/Main Dish, Rice Dishes, Swallow, Sides, Drinks)
- **Cart & Checkout** — Stripe-powered payment processing
- **Delivery / Pickup** — Customer selects at checkout
- **Catering Booking** — Custom catering request form
- **Reviews & Contact** — Customer feedback and inquiry forms

## 🏗️ Architecture
```
CloudFront (CDN + HTTPS)
    ↓
ALB (2 public subnets, secret header verification)
    ↓
EC2 (private subnet, no SSH, SSM Session Manager access)
    ↓
Secrets Manager (Stripe API keys)
```

## 📁 Project Structure
```
recca-kitchen/
├── reccas-template.yaml   # CloudFormation infrastructure template
├── app.py                 # Python Flask backend (API + serving)
├── index.html             # Frontend (single-page application)
├── requirements.txt       # Python dependencies
├── static/                # CSS, JS, images
├── templates/             # Jinja templates (if any)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🚀 Deployment
Deployed via AWS CloudFormation in `us-east-1`.

### Key AWS Resources:
| Resource | Details |
|----------|---------|
| CloudFront | Distribution `E21TNPZR9U7JQK` |
| ALB | Public subnets, secret header gate |
| EC2 | Private subnet, SSM access only |
| Secrets Manager | `ReccasKitchen/StripeSecretKey` |

### Redeploying
```bash
aws cloudformation deploy \
  --template-file reccas-template.yaml \
  --stack-name reccas-kitchen \
  --region us-east-1 \
  --capabilities CAPABILITY_NAMED_IAM
```

## 🔒 Security
- No SSH access — EC2 managed via SSM Session Manager
- EC2 in private subnet (no public IP)
- ALB restricted via CloudFront secret header verification
- Stripe keys stored in AWS Secrets Manager (never in code)
- IAM scoped to least privilege

## 📋 Menu Categories
| Category | Items |
|----------|-------|
| Starters | 6 items (Pepper Soup, Suya, Nkwobi, etc.) |
| Soups / Main Dish | 9 items (Egusi, Efo Riro, etc.) |
| Rice Dishes | 3 items (Jollof Rice, etc.) |
| Swallow | 5 items (Pounded Yam, etc.) |
| Sides | 3 items (Fried Plantain, Moi Moi, Coleslaw) |
| Drinks | 5 items (Chapman, Zobo, Palm Wine, etc.) |

## 📄 License
Private — All rights reserved.
