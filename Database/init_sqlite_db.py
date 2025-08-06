#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据库初始化脚本
创建image_info.db数据库和image_info表结构
"""

import sqlite3
import os
from datetime import datetime

def create_sqlite_database():
    """
    创建SQLite数据库和image_info表
    """
    db_path = os.path.join(os.path.dirname(__file__), 'image_info.db')
    
    # 检查数据库文件是否已存在
    if os.path.exists(db_path):
        user_input = input(f"⚠️  数据库文件已存在: {db_path}\n是否要删除并重新创建? (y/N): ")
        if user_input.lower() in ['y', 'yes']:
            os.remove(db_path)
            print(f"🗑️  删除已存在的数据库文件: {db_path}")
        else:
            print("❌ 操作已取消")
            return None
    
    # 创建SQLite连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建image_info表，字段结构与MySQL保持一致
    create_table_sql = """
    CREATE TABLE image_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object TEXT NOT NULL,
        animal TEXT NOT NULL,
        count INTEGER,
        behavior TEXT,
        status TEXT,
        percentage INTEGER,
        confidence INTEGER,
        image_id TEXT,
        sensor_id TEXT,
        location TEXT,
        longitude TEXT,
        latitude TEXT,
        time TEXT,
        date TEXT,
        caption TEXT,
        type TEXT,
        path TEXT
    );
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    
    print(f"✅ 成功创建SQLite数据库: {db_path}")
    print("✅ 成功创建image_info表")
    
    # 显示表结构
    cursor.execute("PRAGMA table_info(image_info);")
    columns = cursor.fetchall()
    print(f"\n📊 image_info表结构:")
    print("-" * 60)
    for col in columns:
        col_id, name, data_type, not_null, default_val, pk = col
        null_info = "NOT NULL" if not_null else "NULL"
        print(f"字段: {name:<15} 类型: {data_type:<15} 约束: {null_info}")
    
    conn.close()
    return db_path

def verify_database_structure():
    """
    验证数据库结构
    """
    db_path = os.path.join(os.path.dirname(__file__), 'image_info.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_info';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ image_info表存在")
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(image_info);")
            columns = cursor.fetchall()
            print(f"✅ 表包含 {len(columns)} 个字段")
            
            # 检查记录数
            cursor.execute("SELECT COUNT(*) FROM image_info")
            count = cursor.fetchone()[0]
            print(f"📊 当前记录数: {count}")
            
        else:
            print("❌ image_info表不存在")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        return False

def main():
    """
    主函数
    """
    print("🚀 SQLite数据库初始化...")
    print("=" * 60)
    
    try:
        # 创建数据库
        db_path = create_sqlite_database()
        
        if db_path:
            print("\n" + "=" * 60)
            print("🔍 验证数据库结构:")
            verify_database_structure()
            
            print("\n" + "=" * 60)
            print(f"✅ 数据库初始化完成! 位置: {db_path}")
            print("💡 现在可以运行数据迁移脚本来导入数据")
        
    except Exception as e:
        print(f"❌ 初始化过程中发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()