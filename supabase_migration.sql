-- supabase_migration.sql
-- Run this in Supabase SQL Editor to create the tables

CREATE TABLE IF NOT EXISTS food_library (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    kcal_per_100g REAL NOT NULL,
    category TEXT DEFAULT 'other',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meal_records (
    id BIGSERIAL PRIMARY KEY,
    food_name TEXT NOT NULL,
    weight_grams INTEGER NOT NULL,
    kcal REAL NOT NULL,
    meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')) DEFAULT 'lunch',
    image_url TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gender TEXT DEFAULT 'male',
    age INTEGER DEFAULT 25,
    height_cm REAL DEFAULT 170,
    weight_kg REAL DEFAULT 70,
    target_weight_kg REAL DEFAULT 70,
    goal TEXT DEFAULT 'maintain',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed common foods (Chinese cuisine focused)
INSERT INTO food_library (name, kcal_per_100g, category) VALUES
    ('米饭', 116, 'staple'),
    ('馒头', 223, 'staple'),
    ('面条', 137, 'staple'),
    ('全麦面包', 247, 'staple'),
    ('燕麦', 367, 'staple'),
    ('红薯', 86, 'staple'),
    ('鸡胸肉', 133, 'meat'),
    ('鸡腿', 181, 'meat'),
    ('猪肉', 242, 'meat'),
    ('牛肉', 125, 'meat'),
    ('羊肉', 203, 'meat'),
    ('三文鱼', 208, 'meat'),
    ('虾仁', 99, 'meat'),
    ('鸡蛋', 144, 'meat'),
    ('西兰花', 34, 'vegetable'),
    ('菠菜', 23, 'vegetable'),
    ('番茄', 18, 'vegetable'),
    ('黄瓜', 15, 'vegetable'),
    ('胡萝卜', 37, 'vegetable'),
    ('生菜', 15, 'vegetable'),
    ('苹果', 52, 'fruit'),
    ('香蕉', 89, 'fruit'),
    ('橙子', 47, 'fruit'),
    ('葡萄', 67, 'fruit'),
    ('草莓', 32, 'fruit'),
    ('牛奶', 64, 'drink'),
    ('豆浆', 31, 'drink'),
    ('可乐', 42, 'drink'),
    ('橙汁', 45, 'drink'),
    ('纯净水', 0, 'drink'),
    ('薯片', 536, 'snack'),
    ('巧克力', 546, 'snack'),
    ('坚果', 607, 'snack'),
    ('酸奶', 63, 'snack'),
    ('冰淇淋', 207, 'snack')
ON CONFLICT DO NOTHING;
