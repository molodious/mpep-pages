# MPEP Pages

Source files and deploy tooling for [mechanicalpeexamprep.com](https://mechanicalpeexamprep.com) product pages.

Each file is a standalone HTML page. Pushing a change to `main` automatically deploys only the changed pages to WordPress via GitHub Actions.

---

## Page Inventory

| File | Title | Live URL | WP ID |
|---|---|---|---|
| `hvac-bundle.html` | HVAC & Refrigeration Full Access Bundle | [/hvac-and-refrigeration-full-access-bundle/](https://mechanicalpeexamprep.com/hvac-and-refrigeration-full-access-bundle/) | 1029 |
| `tfs-bundle.html` | TFS Full Access Bundle | [/thermal-and-fluids-systems-full-access-bundle/](https://mechanicalpeexamprep.com/thermal-and-fluids-systems-full-access-bundle/) | 1336 |
| `fe.html` | FE Mechanical Exam Prep | [/fe-mechanical-exam-prep-course/](https://mechanicalpeexamprep.com/fe-mechanical-exam-prep-course/) | 2400 |
| `cse.html` | Critical Systems Engineering | [/critical-systems-engineering/](https://mechanicalpeexamprep.com/critical-systems-engineering/) | 3540 |
| `hvac-ebook.html` | HVAC Practice Problems eBook | [/hvac-practice-problems-ebook/](https://mechanicalpeexamprep.com/hvac-practice-problems-ebook/) | 3640 |
| `tfs-ebook.html` | TFS Practice Problems eBook | [/tfs-practice-problems-ebook/](https://mechanicalpeexamprep.com/tfs-practice-problems-ebook/) | 3641 |
| `fundamentals.html` | Mechanical PE Fundamentals | [/mechanical-pe-fundamentals/](https://mechanicalpeexamprep.com/mechanical-pe-fundamentals/) | 3639 |
| `dip.html` | Daily Insights Premium | [/daily-insights-premium/](https://mechanicalpeexamprep.com/daily-insights-premium/) | 3634 |

---

## Workflow

**Edit → Commit → Push → Live**

1. Edit the HTML file directly (it's a self-contained page — open in a browser to preview)
2. Commit with a clear message: `git commit -m "TFS bundle: update testimonial"`
3. Push to main: `git push`
4. GitHub Actions detects which files changed and deploys only those (~60 seconds)

That's it. The live site reflects whatever is in `main`.

---

## Rollback

To revert a page to a previous version:

```bash
# See the history for a file
git log --oneline -- hvac-bundle.html

# Restore a specific version
git checkout abc1234 -- hvac-bundle.html

# Commit and push — Actions will redeploy it
git commit -m "Revert hvac-bundle to version before testimonial change"
git push
```

---

## GitHub Actions Setup

The workflow file is at `.github/workflows/deploy.yml`. It requires one GitHub Secret:

| Secret | Value |
|---|---|
| `WP_PASSWORD` | WordPress application password for user `dan` |

To add: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

---

## Shared Patterns

These patterns appear across multiple pages. When making a change that affects a shared pattern, check which pages use it and update all of them.

### Stripe checkout button
```html
<a href="#" class="btn btn-red mpep-stripe-btn" style="color:#fff!important;text-decoration:none!important;">
  Enroll Now
</a>
```
The JS at the bottom of each page intercepts clicks on `.mpep-stripe-btn` and POSTs to the checkout endpoint:
```js
fetch('https://btc.mechanicalpeexamprep.com/create-checkout-session-product', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({productId: 'PRODUCT_ID'})
})
```
Each page has its own `productId`. See `pages.json` for which page maps to which product.

### Bitcoin button
```html
<a href="https://mechanicalpeexamprep.com/btcpay-checkout/?product=PRODUCT_ID"
   class="btn btn-orange"
   style="color:#fff!important;text-decoration:none!important;">
  <span class="btn-main">Save 10%</span>
  <span class="btn-sub">Pay with Bitcoin</span>
</a>
```

### Email Dan link
```html
<a href="#" onclick="window.location='mailto:dan@mechanicalpeexamprep.com';return false;">
  Email Dan
</a>
```
Uses `onclick` instead of `href="mailto:..."` to bypass Cloudflare's email obfuscation.

### CTA section button (inverted)
In the bottom CTA section (dark/gradient background), the primary button inverts to white background with accent-colored text:
```html
<a href="#" class="btn btn-red mpep-stripe-btn"
   style="background-color:#fff!important;color:#dd2743!important;text-decoration:none!important;">
  Enroll Now
</a>
```
The accent color varies by page: `#dd2743` (red) for most, `#2d7a4f` (green) for CSE, `#4c1d95` (indigo) for FE.

### Dan's photo (circular crop)
The border/circle shape lives on the wrapper div, not the img tag — this prevents WordPress theme CSS from distorting the image:
```html
<div style="flex-shrink:0;width:110px;height:110px;border-radius:50%;border:3px solid ACCENT_COLOR;overflow:hidden;">
    <img src="https://mechanicalpeexamprep.com/wp-content/uploads/2020/05/Dan-Profile.png"
         alt="Dan Molloy, PE"
         style="width:100%;height:100%;object-fit:cover;display:block;">
</div>
```

---

## WordPress Notes

- **No transforms at deploy time.** `deploy_ci.py` wraps the file in a `<!-- wp:html -->` block and pushes it. Nothing else changes. What's in the file is what goes live.
- **Elementor cache is cleared automatically** after every deploy.
- **`object-fit` must be an inline style**, not inside a `<style>` block. WordPress strips it from `<style>` blocks.
- **Button link colors must be inline styles.** The WordPress theme overrides `<a>` colors. Always include `color:#fff!important;text-decoration:none!important;` on button links.
- **No draft mode.** Changes go directly to the published page.
