#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 sql_query 模块的示例
"""

from sql_query import query_sql

def test_basic_query():
    """测试基本查询功能"""
    print("=== 测试基本查询功能 ===")
    
    # 测试查询所有数据
    sql1 = "SELECT * FROM 国家重点保护野生动物名录 LIMIT 5;"
    print(f"执行SQL: {sql1}")
    result1 = query_sql(sql1)
    print(f"结果: {result1}")
    print()

def test_specific_query():
    """测试特定条件查询"""
    print("=== 测试特定条件查询 ===")
    
    # 测试按中文名查询
    sql2 = "SELECT * FROM 国家重点保护野生动物名录 WHERE 中文名 = '马';"
    print(f"执行SQL: {sql2}")
    result2 = query_sql(sql2)
    print(f"结果: {result2}")
    print()

def test_count_query():
    """测试计数查询"""
    print("=== 测试计数查询 ===")
    
    # 测试计数查询
    sql3 = "SELECT COUNT(*) as total FROM 国家重点保护野生动物名录;"
    print(f"执行SQL: {sql3}")
    result3 = query_sql(sql3)
    print(f"结果: {result3}")
    print()

def test_protection_level_query():
    """测试按保护级别查询"""
    print("=== 测试按保护级别查询 ===")
    
    # 测试按保护级别查询
    sql4 = "SELECT 中文名, 保护级别 FROM 国家重点保护野生动物名录 WHERE 保护级别 = 'I' LIMIT 3;"
    print(f"执行SQL: {sql4}")
    result4 = query_sql(sql4)
    print(f"结果: {result4}")
    print()

def test_invalid_query():
    """测试无效查询"""
    print("=== 测试无效查询 ===")
    
    # 测试非SELECT语句（应该被拒绝）
    sql5 = "INSERT INTO test_table VALUES (1, 'test');"
    print(f"执行SQL: {sql5}")
    result5 = query_sql(sql5)
    print(f"结果: {result5}")
    print()
    
    # 测试语法错误的SQL
    sql6 = "SELECT * FORM 国家重点保护野生动物名录;"  # 故意写错FORM
    print(f"执行SQL: {sql6}")
    result6 = query_sql(sql6)
    print(f"结果: {result6}")
    print()

def test_table_structure():
    """测试查看表结构"""
    print("=== 测试查看表结构 ===")
    
    # 查看表结构
    sql7 = "PRAGMA table_info(国家重点保护野生动物名录);"
    print(f"执行SQL: {sql7}")
    result7 = query_sql(sql7)
    print(f"结果: {result7}")
    print()

if __name__ == "__main__":
    print("开始测试 sql_query 模块...")
    print("=" * 50)
    
    try:
        test_basic_query()
        test_specific_query()
        test_count_query()
        test_protection_level_query()
        test_table_structure()
        test_invalid_query()
        
        print("=" * 50)
        print("测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")