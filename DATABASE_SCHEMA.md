# Database Schema Documentation

## 📊 Entity Relationship Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   areas     │    │ locations   │    │    users    │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │◄──┐│ id (PK)     │◄──┐│ id (PK)     │
│ name        │   ││ country     │   ││ display_name│
│ center_lat  │   ││ state       │   ││ username    │
│ center_lng  │   ││ district    │   ││ phone       │
│ radius_m    │   ││ city        │   ││ email       │
│ created_at  │   ││ postal_code │   ││ avatar_url  │
└─────────────┘   ││ address_line│   ││ bio         │
                  ││ latitude    │   ││ location_id │──┘
                  ││ longitude   │   ││ area_id     │──┘
                  ││ created_at  │   ││ password_hash│
                  │└─────────────┘   ││ is_verified │
                  │                  ││ created_at  │
                  │                  │└─────────────┘
                  │                  │       │
                  │                  │       │ 1:N
                  │                  │       ▼
┌─────────────┐   │  ┌─────────────┐ │ ┌─────────────┐
│post_images  │   │  │    posts    │ │ │   likes     │
├─────────────┤   │  ├─────────────┤ │ ├─────────────┤
│ id (PK)     │   │  │ id (PK)     │ │ │ id (PK)     │
│ post_id (FK)│──┐│  │ user_id (FK)│─┘ │ post_id (FK)│──┐
│ url         │  ││  │ area_id (FK)│───┘ user_id (FK)│  │
│ order_idx   │  ││  │ location_id │─────┘created_at │  │
│ created_at  │  ││  │ text        │     └─────────────┘  │
└─────────────┘  ││  │ category    │                      │
                 ││  │ lat         │     ┌─────────────┐  │
                 ││  │ lng         │     │ wishlists   │  │
                 ││  │ event_time  │     ├─────────────┤  │
                 ││  │ created_at  │     │ id (PK)     │  │
                 ││  │ updated_at  │     │ post_id (FK)│──┘
                 ││  │ is_deleted  │     │ user_id (FK)│
                 ││  └─────────────┘     │ created_at  │
                 ││         │            └─────────────┘
                 ││         │ 1:N
                 ││         ▼            ┌─────────────┐
                 ││  ┌─────────────┐     │  comments   │
                 ││  │   joins     │     ├─────────────┤
                 ││  ├─────────────┤     │ id (PK)     │
                 ││  │ id (PK)     │     │ post_id (FK)│──┐
                 ││  │ post_id (FK)│──┐  │ user_id (FK)│  │
                 ││  │ user_id (FK)│  │  │ text        │  │
                 ││  │ created_at  │  │  │ created_at  │  │
                 ││  └─────────────┘  │  └─────────────┘  │
                 │└───────────────────┘                   │
                 └─────────────────────────────────────────┘

                           ┌─────────────┐
                           │   reports   │
                           ├─────────────┤
                           │ id (PK)     │
                           │ reporter_id │
                           │ post_id (FK)│
                           │ user_id (FK)│
                           │ reason      │
                           │ description │
                           │ created_at  │
                           └─────────────┘
```

## 📋 Table Specifications

### 🏠 Core Tables

#### users
**Purpose**: Store user accounts and profiles
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,              -- UUID: "user_123e4567"
    display_name TEXT NOT NULL,       -- "John Doe"
    username TEXT UNIQUE NOT NULL,    -- "johndoe" (unique)
    phone TEXT,                       -- "+1234567890" (optional)
    email TEXT,                       -- "john@example.com" (optional)
    avatar_url TEXT,                  -- "https://cdn.example.com/avatar.jpg"
    bio TEXT,                         -- "Local community enthusiast"
    location_id TEXT,                 -- FK to locations table
    area_id TEXT,                     -- FK to areas table
    password_hash TEXT NOT NULL,      -- bcrypt hashed password
    is_verified INTEGER DEFAULT 0,    -- 0=unverified, 1=verified
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### areas
**Purpose**: Define geographic community boundaries
```sql
CREATE TABLE areas (
    id TEXT PRIMARY KEY,              -- "area_downtown_001"
    name TEXT NOT NULL,               -- "Downtown District"
    center_lat REAL NOT NULL,         -- 12.9716 (latitude)
    center_lng REAL NOT NULL,         -- 77.5946 (longitude)
    radius_m INTEGER NOT NULL,        -- 5000 (radius in meters)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### posts
**Purpose**: Store community posts and events
```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,              -- UUID: "post_123e4567"
    user_id TEXT NOT NULL,            -- FK to users table
    area_id TEXT NOT NULL,            -- FK to areas table
    location_id TEXT,                 -- FK to locations (optional)
    text TEXT NOT NULL,               -- "New coffee shop opening!"
    category TEXT NOT NULL,           -- "business", "event", "social"
    lat REAL,                         -- GPS latitude (optional)
    lng REAL,                         -- GPS longitude (optional)
    event_time DATETIME,              -- Event date/time (for events)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0      -- Soft delete: 0=active, 1=deleted
);
```

### 📍 Location Tables

#### locations
**Purpose**: Store detailed address information
```sql
CREATE TABLE locations (
    id TEXT PRIMARY KEY,              -- "loc_123e4567"
    country TEXT,                     -- "India"
    state TEXT,                       -- "Karnataka"
    district TEXT,                    -- "Bangalore Urban"
    city TEXT,                        -- "Bangalore"
    postal_code TEXT,                 -- "560001"
    address_line TEXT,                -- "123 MG Road, Brigade Road"
    latitude REAL,                    -- 12.9716
    longitude REAL,                   -- 77.5946
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 🎯 Interaction Tables

#### likes
**Purpose**: Track post likes/reactions
```sql
CREATE TABLE likes (
    id TEXT PRIMARY KEY,              -- "like_123e4567"
    post_id TEXT NOT NULL,            -- FK to posts
    user_id TEXT NOT NULL,            -- FK to users
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)          -- One like per user per post
);
```

#### comments
**Purpose**: Store post comments and discussions
```sql
CREATE TABLE comments (
    id TEXT PRIMARY KEY,              -- "comment_123e4567"
    post_id TEXT NOT NULL,            -- FK to posts
    user_id TEXT NOT NULL,            -- FK to users
    text TEXT NOT NULL,               -- "Great initiative!"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### wishlists
**Purpose**: User bookmarked/saved posts
```sql
CREATE TABLE wishlists (
    id TEXT PRIMARY KEY,              -- "wishlist_123e4567"
    post_id TEXT NOT NULL,            -- FK to posts
    user_id TEXT NOT NULL,            -- FK to users
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)          -- One bookmark per user per post
);
```

### 🎪 Event Tables

#### joins
**Purpose**: Track event participation/attendance
```sql
CREATE TABLE joins (
    id TEXT PRIMARY KEY,              -- "join_123e4567"
    post_id TEXT NOT NULL,            -- FK to posts (event posts)
    user_id TEXT NOT NULL,            -- FK to users
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)          -- One join per user per event
);
```

### 🖼️ Media Tables

#### post_images
**Purpose**: Store multiple images per post
```sql
CREATE TABLE post_images (
    id TEXT PRIMARY KEY,              -- "img_123e4567"
    post_id TEXT NOT NULL,            -- FK to posts
    url TEXT NOT NULL,                -- "https://cdn.example.com/image.jpg"
    order_idx INTEGER DEFAULT 0,      -- Display order: 0, 1, 2...
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 🚨 Moderation Tables

#### reports
**Purpose**: Content moderation and user reports
```sql
CREATE TABLE reports (
    id TEXT PRIMARY KEY,              -- "report_123e4567"
    reporter_id TEXT NOT NULL,        -- FK to users (who reported)
    post_id TEXT,                     -- FK to posts (optional)
    user_id TEXT,                     -- FK to users (optional)
    reason TEXT NOT NULL,             -- "spam", "inappropriate", "fake"
    description TEXT,                 -- Additional details
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Database Indexes

Performance optimization indexes:
```sql
-- Post queries by area and time
CREATE INDEX idx_posts_area_created ON posts(area_id, created_at DESC);

-- User's posts
CREATE INDEX idx_posts_user ON posts(user_id);

-- Post engagement
CREATE INDEX idx_likes_post ON likes(post_id);
CREATE INDEX idx_comments_post ON comments(post_id);

-- Geographic queries
CREATE INDEX idx_areas_location ON areas(center_lat, center_lng);
```

## 📊 Data Relationships

### One-to-Many Relationships
- `users` → `posts` (one user, many posts)
- `posts` → `comments` (one post, many comments)
- `posts` → `likes` (one post, many likes)
- `posts` → `post_images` (one post, many images)
- `areas` → `users` (one area, many users)
- `areas` → `posts` (one area, many posts)

### Many-to-Many Relationships
- `users` ↔ `posts` (via `likes` table)
- `users` ↔ `posts` (via `wishlists` table)
- `users` ↔ `posts` (via `joins` table for events)

### Optional Relationships
- `users` → `locations` (user may have location)
- `posts` → `locations` (post may have specific location)

## 🎯 Post Categories

Supported categories in `posts.category`:
- `event` - Community events, meetups, gatherings
- `business` - Business openings, promotions, services
- `sports` - Sports activities, games, tournaments
- `social` - Social gatherings, parties, casual meetups
- `help` - Help requests, assistance needed
- `announcement` - General community announcements
- `lost_found` - Lost and found items
- `marketplace` - Buy/sell items locally

## 🔒 Data Constraints

### Required Fields
- `users`: `display_name`, `username`, `password_hash`
- `posts`: `user_id`, `area_id`, `text`, `category`
- `areas`: `name`, `center_lat`, `center_lng`, `radius_m`

### Unique Constraints
- `users.username` - No duplicate usernames
- `likes(post_id, user_id)` - One like per user per post
- `wishlists(post_id, user_id)` - One bookmark per user per post
- `joins(post_id, user_id)` - One join per user per event

### Soft Deletes
- `posts.is_deleted` - Posts are soft deleted (marked as deleted but not removed)
- Allows for data recovery and audit trails

## 📈 Sample Data Sizes

Estimated storage for community app:
- **Small Community** (1K users): ~50MB
- **Medium Community** (10K users): ~500MB  
- **Large Community** (100K users): ~5GB

Per table estimates (10K users):
- `users`: ~2MB (200 bytes/user)
- `posts`: ~200MB (2KB/post, 100 posts/user)
- `comments`: ~100MB (500 bytes/comment)
- `likes`: ~20MB (20 bytes/like)
- `post_images`: ~150MB (metadata only, images stored externally)