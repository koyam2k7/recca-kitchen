# Recca's Kitchen

Restaurant ordering site (menu, cart, Stripe test-mode checkout, catering enquiries) deployed on AWS.

## Architecture

```
Viewer ──HTTPS──> CloudFront ──HTTP (+ secret header)──> ALB ──> EC2 (private subnet)
                                                                   │
                                                    Flask app (:5000) behind Apache (:80)
                                                                   │
                                              Secrets Manager (Stripe secret key) + S3 (app files)
```

- **CloudFront** terminates HTTPS and injects a secret origin header (`X-Origin-Verify`) so the ALB origin only serves requests coming through the distribution.
- **ALB** (public subnets) forwards HTTP to the EC2 instance.
- **EC2** runs in a **private subnet** (egress via NAT gateway). Apache enforces the secret header for all paths except `/health`, and reverse-proxies `/api/*` to the Flask app on port 5000.
- **IAM role** grants the instance read access to the Stripe secret in Secrets Manager and to the app files in S3.
- **SSM Session Manager** is used for shell access (no SSH, no public IP).

## Repository layout

```
infrastructure/reccas-kitchen.yaml   CloudFormation template (full stack)
app/app.py                           Flask backend (menu + Stripe checkout + catering)
app/index.html                       Frontend single-page site
app/requirements.txt                 Python dependencies
```

## Prerequisites

1. A Stripe **secret** key stored in Secrets Manager:
   ```
   aws secretsmanager create-secret \
     --name ReccasKitchen/StripeSecretKey \
     --secret-string "sk_test_..." \
     --region us-east-1
   ```
2. An S3 bucket holding `app.py` and `index.html`:
   ```
   aws s3 cp app/app.py       s3://<your-app-bucket>/app.py
   aws s3 cp app/index.html   s3://<your-app-bucket>/index.html
   ```

## Deploy

```
aws cloudformation deploy \
  --template-file infrastructure/reccas-kitchen.yaml \
  --stack-name ReccasKitchen \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      AppBucket=<your-app-bucket> \
      CloudFrontSecretValue=<a-strong-random-string> \
  --region us-east-1
```

The site URL is emitted as the `SiteURL` stack output.

## Notes on secrets

- `app/app.py` contains only a Stripe **publishable** test key (`pk_test_...`), which is designed to be public.
- The Stripe **secret** key is never in source — it is loaded at runtime from Secrets Manager.
- `CloudFrontSecretValue` is a `NoEcho` parameter; supply a strong random value at deploy time and do not commit it.
