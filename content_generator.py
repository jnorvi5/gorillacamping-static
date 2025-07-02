import requests
import json
import time
import random

# This script scrapes top camping content from Reddit
# and formats it for your blog with affiliate links

def get_reddit_content(subreddit, time_filter="month", limit=10):
    headers = {
        'User-Agent': 'Gorilla Camping Research Script/1.0'
    }
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t={time_filter}&limit={limit}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        posts = []
        
        for post in data['data']['children']:
            posts.append({
                'title': post['data']['title'],
                'url': f"https://reddit.com{post['data']['permalink']}",
                'score': post['data']['score'],
                'num_comments': post['data']['num_comments'],
                'created_utc': post['data']['created_utc']
            })
        
        return posts
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def generate_blog_post(post, affiliate_products):
    title = f"Gorilla Review: {post['title']}"
    
    # Create article structure
    content = f"""
# {title}

![Camping Gear](https://example.com/images/camping-gear.jpg)

I recently came across an interesting discussion about {post['title'].lower()}. This got me thinking about the best gear for this situation and how to approach it with a guerilla mindset.

## The Gorilla Approach

When facing {post['title'].lower()}, I always consider these factors:

1. Minimalist setup that doesn't break the bank
2. Multi-purpose gear that earns its keep
3. Off-grid capabilities for true freedom

## Top Gear Recommendations

Based on my personal testing and experience, here are the items that have performed exceptionally well:
"""

    # Add affiliate products
    for product in random.sample(affiliate_products, 2):
        content += f"""
### {product['name']}

![{product['name']}]({product['image']})

**Price:** ~~${product['old_price']}~~ **${product['price']}** (Save ${int(float(product['old_price'])) - int(float(product['price']))})

{product['description']}

[CHECK PRICE ON AMAZON →]({product['affiliate_link']})

"""

    content += f"""
## Conclusion

Whether you're dealing with {post['title'].lower()} or just preparing for your next adventure, these tools will serve you well.

*Have you tried any of these items? Let me know in the comments below!*

*Original discussion inspired by [this Reddit thread]({post['url']})*
"""
    
    return {
        'title': title,
        'content': content,
        'source': post['url'],
        'tags': ['gear review', 'camping tips', 'affiliate', 'gorilla camping']
    }

if __name__ == "__main__":
    # Sample affiliate products
    affiliate_products = [
        {
            'name': 'Jackery Explorer 240',
            'image': 'https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg',
            'description': 'This power station is perfect for keeping your devices charged while camping off-grid. I\'ve used it for over 6 months and it\'s been essential for my content creation.',
            'price': '199.99',
            'old_price': '299.99',
            'affiliate_link': 'https://amzn.to/yourlink'
        },
        {
            'name': 'LifeStraw Personal Water Filter',
            'image': 'https://m.media-amazon.com/images/I/71SYsNwj7hL._AC_UL320_.jpg',
            'description': 'The LifeStraw has saved me countless times when camping in remote locations. It filters 99.9999% of waterborne bacteria and parasites.',
            'price': '14.96',
            'old_price': '19.95',
            'affiliate_link': 'https://amzn.to/yourlink'
        },
        # Add more products as needed
    ]
    
    # Get content from camping-related subreddits
    subreddits = ['camping', 'CampingGear', 'vandwellers', 'preppers', 'survival']
    all_posts = []
    
    for sub in subreddits:
        posts = get_reddit_content(sub)
        all_posts.extend(posts)
        time.sleep(2)  # Be nice to Reddit API
    
    # Generate blog posts from Reddit content
    blog_posts = []
    for post in all_posts[:5]:  # Generate 5 posts
        blog_post = generate_blog_post(post, affiliate_products)
        blog_posts.append(blog_post)
        
    # Save generated content
    with open('generated_posts.json', 'w') as f:
        json.dump(blog_posts, f, indent=2)
        
    print(f"Generated {len(blog_posts)} blog posts. Check generated_posts.json")
