import mysql.connector

def open_database_connection():
    mydb = mysql.connector.connect(user='root', password='020101051', host='localhost', database='QLTK')
    return mydb

def run_query(query, params):
    mydb = open_database_connection()
    cursor = mydb.cursor()
    # Thực thi truy vấn với tham số
    cursor.execute(query, params)
    # Lấy tất cả các kết quả và trả về dưới dạng danh sách
    result = cursor.fetchall()
    mydb.close()
    return result

def add_tai_khoan(tai_khoan, mat_khau):
    mydb = open_database_connection()
    cursor = mydb.cursor()

    # Tạo chuỗi truy vấn SQL để thêm dữ liệu
    sql_query = "INSERT INTO TaiKhoan (taiKhoan, matKhau) VALUES (%s, %s)"

    # Thực thi truy vấn với các giá trị trong tham số 'values'
    values = (tai_khoan, mat_khau)
    cursor.execute(sql_query, values)
    mydb.commit()
    mydb.close()

def add_du_lieu(cauHoi, dapAn , taiKhoan):
    mydb = open_database_connection()
    cursor = mydb.cursor()

    # Tạo chuỗi truy vấn SQL để thêm dữ liệu
    sql_query = "INSERT INTO DuLieu(cauHoi , dapAn , taiKhoan) VALUES (%s,%s,%s);"

    # Thực thi truy vấn với các giá trị trong tham số 'values'
    values = (cauHoi, dapAn , taiKhoan)
    cursor.execute(sql_query, values)
    mydb.commit()
    mydb.close()

def delete_data_by_tai_khoan(tai_khoan):
    mydb = open_database_connection()
    cursor = mydb.cursor()

    # Tạo chuỗi truy vấn SQL để xóa dữ liệu
    sql_query = "DELETE FROM QLTK.DuLieu WHERE taiKhoan = %s"

    # Thực thi truy vấn với các giá trị trong tham số 'values'
    values = (tai_khoan,)
    cursor.execute(sql_query, values)
    mydb.commit()
    mydb.close()

