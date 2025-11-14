-- -----------------------------------
-- 1) Countries
-- -----------------------------------
CREATE TABLE IF NOT EXISTS countries (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- -----------------------------------
-- 2) States
-- -----------------------------------
CREATE TABLE IF NOT EXISTS states (
  id TEXT PRIMARY KEY,
  country_id TEXT NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE
);

-- -----------------------------------
-- 3) Districts
-- -----------------------------------
CREATE TABLE IF NOT EXISTS districts (
  id TEXT PRIMARY KEY,
  state_id TEXT NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE CASCADE
);

-- -----------------------------------
-- 4) Cities
-- -----------------------------------
CREATE TABLE IF NOT EXISTS cities (
  id TEXT PRIMARY KEY,
  state_id TEXT,
  district_id TEXT,
  name TEXT NOT NULL,
  FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE SET NULL,
  FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE SET NULL
);

-- -----------------------------------
-- 5) Locations (Normalized)
-- -----------------------------------
CREATE TABLE IF NOT EXISTS locations (
  id TEXT PRIMARY KEY,
  country TEXT,
  state TEXT,
  district TEXT,
  city TEXT,
  postal_code TEXT,
  address_line TEXT,
  city_id TEXT,
  latitude REAL,
  longitude REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL
);

-- -----------------------------------
-- 6) Users
-- -----------------------------------
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  phone TEXT,
  email TEXT,
  avatar_url TEXT,
  bio TEXT,
  location_id TEXT,
  password_hash TEXT NOT NULL,
  is_verified INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- -----------------------------------
-- 7) Posts (no lat/lng here)
-- -----------------------------------
CREATE TABLE IF NOT EXISTS posts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  location_id TEXT,
  text TEXT NOT NULL,
  category TEXT NOT NULL,
  event_time DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_deleted INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- -----------------------------------
-- 8) Post Images
-- -----------------------------------
CREATE TABLE IF NOT EXISTS post_images (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL,
  url TEXT NOT NULL,
  order_idx INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- -----------------------------------
-- 9) Likes
-- -----------------------------------
CREATE TABLE IF NOT EXISTS likes (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(post_id, user_id)
);

-- -----------------------------------
-- 10) Wishlist (Saved Posts)
-- -----------------------------------
CREATE TABLE IF NOT EXISTS wishlists (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(post_id, user_id)
);

-- -----------------------------------
-- 11) Comments
-- -----------------------------------
CREATE TABLE IF NOT EXISTS comments (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  text TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -----------------------------------
-- 12) Reports
-- -----------------------------------
CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  reporter_id TEXT NOT NULL,
  post_id TEXT,
  reported_user_id TEXT,
  reason TEXT NOT NULL,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -----------------------------------
-- 13) Joins (Users joining an event post)
-- -----------------------------------
CREATE TABLE IF NOT EXISTS joins (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(post_id, user_id)
);

-- -----------------------------------
-- 14) Indexes
-- -----------------------------------
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city);
CREATE INDEX IF NOT EXISTS idx_posts_user_created ON posts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id);

-- -----------------------------------
-- 15) Trigger for updated_at sync
-- -----------------------------------
DROP TRIGGER IF EXISTS trg_posts_updated_at;
CREATE TRIGGER trg_posts_updated_at
AFTER UPDATE ON posts
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
  UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- -----------------------------------
-- Sample Data
-- -----------------------------------
INSERT OR IGNORE INTO locations (id, country, state, city, latitude, longitude) VALUES 
('loc1', 'India', 'Karnataka', 'Bangalore', 12.9716, 77.5946);

INSERT OR IGNORE INTO users (id, username, password_hash, location_id) VALUES 
('user1', 'testuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9w5KS', 'loc1');

INSERT OR IGNORE INTO posts (id, user_id, location_id, text, category) VALUES 
('post1', 'user1', 'loc1', 'Welcome to our community!', 'announcement');