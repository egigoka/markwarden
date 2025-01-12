import sys
import os
import sqlite3
from pathlib import Path
from typing import Optional

def init_db_v1(db_path: Path) -> None:
    """Initialize database with version 1 schema"""
    
    sql = """
    -- Create DbVersion table and set initial version
    CREATE TABLE IF NOT EXISTS DbVersion (
        version INTEGER PRIMARY KEY
    );
    INSERT OR IGNORE INTO DbVersion (version) VALUES (1);
    
    -- Users table
    CREATE TABLE IF NOT EXISTS Users (
        uuid TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        email_verified BOOLEAN DEFAULT FALSE
    );
    
    -- UserSettings table
    CREATE TABLE IF NOT EXISTS UserSettings (
        user_uuid TEXT,
        setting_name TEXT,
        value TEXT,
        PRIMARY KEY (user_uuid, setting_name),
        FOREIGN KEY (user_uuid) REFERENCES Users(uuid)
    );
    
    -- Bookmarks table
    CREATE TABLE IF NOT EXISTS Bookmarks (
        uuid TEXT PRIMARY KEY,
        user_uuid TEXT NOT NULL,
        url TEXT,
        name TEXT NOT NULL,
        is_folder BOOLEAN,
        parent_uuid TEXT,
        favicon_domain TEXT,
        created_at TIMESTAMP,
        last_visited TIMESTAMP,
        description TEXT,
        order_index INTEGER,
        favorite BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (parent_uuid) REFERENCES Bookmarks(uuid),
        FOREIGN KEY (favicon_domain) REFERENCES Favicons(domain),
        FOREIGN KEY (user_uuid) REFERENCES Users(uuid)
    );
    
    -- Favicons table
    CREATE TABLE IF NOT EXISTS Favicons (
        domain TEXT PRIMARY KEY,
        image BLOB,
        content_type TEXT,
        last_updated TIMESTAMP
    );
    
    -- Tags table
    CREATE TABLE IF NOT EXISTS Tags (
        uuid TEXT PRIMARY KEY,
        user_uuid TEXT NOT NULL,
        name TEXT NOT NULL,
        color TEXT,
        FOREIGN KEY (user_uuid) REFERENCES Users(uuid)
    );
    
    -- BookmarkTags table
    CREATE TABLE IF NOT EXISTS BookmarkTags (
        bookmark_uuid TEXT,
        tag_uuid TEXT,
        PRIMARY KEY (bookmark_uuid, tag_uuid),
        FOREIGN KEY (bookmark_uuid) REFERENCES Bookmarks(uuid),
        FOREIGN KEY (tag_uuid) REFERENCES Tags(uuid)
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);
    CREATE INDEX IF NOT EXISTS idx_users_username ON Users(username);
    
    CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON Bookmarks(user_uuid);
    CREATE INDEX IF NOT EXISTS idx_bookmarks_parent ON Bookmarks(parent_uuid);
    CREATE INDEX IF NOT EXISTS idx_bookmarks_favicon ON Bookmarks(favicon_domain);
    CREATE INDEX IF NOT EXISTS idx_bookmarks_folder ON Bookmarks(user_uuid, is_folder);
    CREATE INDEX IF NOT EXISTS idx_bookmarks_folder_order ON Bookmarks(parent_uuid, order_index);
    CREATE INDEX IF NOT EXISTS idx_bookmarks_favorite ON Bookmarks(user_uuid, favorite);
    
    CREATE INDEX IF NOT EXISTS idx_tags_user ON Tags(user_uuid);
    CREATE INDEX IF NOT EXISTS idx_tags_name ON Tags(user_uuid, name);
    
    CREATE INDEX IF NOT EXISTS idx_bookmarktags_tag ON BookmarkTags(tag_uuid);
    CREATE INDEX IF NOT EXISTS idx_bookmarktags_bookmark ON BookmarkTags(bookmark_uuid);
    
    CREATE INDEX IF NOT EXISTS idx_usersettings_user ON UserSettings(user_uuid);
    """
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.executescript(sql)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        raise

def get_db_version(db_path: Path) -> Optional[int]:
    """Get current database version"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM DbVersion LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Error getting database version: {e}")
        return None


if __name__ == "__main__":

    from dotenv import load_dotenv

    load_dotenv()

    try:
        db_path = Path(os.getenv("BOOKMARKS_DATABASE_PATH"))
    except TypeError:
        db_path = None

    if not db_path:
        print("copy .env.example to .env and fill BOOKMARKS_DATABASE_PATH")
        sys.exit(1)

    version = get_db_version(db_path)
    if not version:
        print("Creating database")
        init_db_v1(db_path)
        version = get_db_version(db_path)
    print(f"Database is at version {version}")
