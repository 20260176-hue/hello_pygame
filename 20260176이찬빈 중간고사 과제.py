import pygame
import random
import sys
import base64
import io

# --- 1. 초기 설정 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
CELL = CELL_SIZE = 20 # 원본 코드의 CELL을 사용
TARGET_FPS = 120 

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  스프라이트 시트 데이터 (비워둠)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHEET_B64 = "iVBORw0KGgoAAAANSUhEUgAAAKAAAADNCAYAAAA/pXupAAAZbElEQVR4Ae2dT2wjyXXGv/eq5w+cPSiBDxNHBx100Mkg1htgDxyb4yXsbEbG6jCHTTKIhViJFXiOg1hJNJIWVhDaGCAXGZBhOlFgIZjDHGRDazsB4+XEPOzBMBhjDzrowIMCzMEI5uBT0F2Vne2uVrPZTTZZ3WSLU59Asatfd7HqvV997yo2Njbx+utv4PXX38Cvfv2RC3Z2BN/YYb6+o1js5DJ2buwwiT3FziMSN3aInR3iazuCr+0iNlbs7GCcj7i+B0fsQji74Ou7ENd24YhdFs6OEs4eyHk0znyCnR12buyxuL6r6PojwcJojCAH4Bs7/vW193DN2YPj7BHfeKT3rj+Rdfi5cK7tgC7XR+zsgYM9iRs7ENfM9y9u7AgWu8qv3R45YleJG7tCXH/EdH2PHPGIxfU9DsfXd0lc39Vjdq7tKrq2K5zBuCKxA8fZg3B2/bVce2/ja1/ff/0PP8efe+MNRX+58dcAgObRkbvxtT+D8gAwAVIhKgJYARLojzMx9T0Yk1SxiRIkAPJIKCgPAoIBBcWQ9PJXJVhxuAYJCQbrKUmOiivpQTIYSgDkSUgSEH6cAA8eAUIBnr8NhZHL7RfD/3XFAAXpAZQE/AllkLMx9j9yv1AAkyR//qH5CPdPAlAp+49IQSF4NlL82FivGVCT7L95dIyN9XUHAGhjYxPNf/2h+/Wv/gl5gBIQCRvyJCD4MiEePDBEZMNSKgj2x4kABDxCkhBCSc/H+DIBAQQhAAmHILH+ORyAWGIBFgwAnoQU8IzGDA8SzGAJSJZ+ikcAkKA0AwCDdfEZ/su6+AwoKcc9UYDwswAPPnSmY11+CQkiASiJ5tEx/mp9/RrRtd9xN776p5pc8qDGW3ABCSAierkRpfy1mI7BzCwlJCCZCFDa7UBESkXHKgv1BYoAItIFU4qUMhqH5WS/MADTpVNRuPfwwAaMC8DHhwUgL91PAOzpg3D51ERqHh1DgMXO65XP6gKAichHmJmIwATSo8BvCMSCiPy4nzYmEAEUbIfDMaDAzExE5APhzwACMQEE1kMQBeef/VMScyZWAeBJ8aHyf1jpPargT/tNdMxERCCCIFDSfglEwUjnY9iYoPztg0kxKSgikOrfP6kwD3otUSc0HYfF7b/o27v+YyICsVBhfVXffnxrIUHEivw90OWYBvIV7p+ZFPXvv/vfvwax8yl3Y/1+7ATEyR4k3Yz9YS01pBpKBiVhpSBZAJAEBbCCBDFJShlfvg8liVg7QtAFyLdlBhRU8DBJQHHoAPGTf1UdkJRiYgJAkFASkiIOGNl/zAEH23LE+XLKTfPoGATnZh+ARbRAYj8jSqpcW+Bh8zk2N27NsmNOQBizBgCKQ/CZpFKKoRQIBDDJAA4/PwogAlQaIHlJAAQSgG8wCsoMNAYERGgAHiTC/Tf/5d9AfO1T3l+s3ycmqQAoKZl1AiRAOknsNz1KPSJTTsDhG03g3efA+UfYPHySOQEs/SYSnniSpAHwOxKRBJHePyvuOxBSZT8gpQRASX+g4QcQ7pHkYP0Dp9TXedY/0QFnkYAoAFIyM0GFcCQk4HCvDbzWufyR/TY2X7SuBADDDkDcAef2AAS1/+ejY0W4flNufPXP+wDoawEk0XcSpA/HrNXc/iXchZ+hsddG77fZ4WMwQAphWyNAAmEHGHDACPxT3D/79Yp0bgAMHwwQABX8h9/XgksI/Uwoj8ECnvTC+YQQAgA8zzOjqwgHTEuBCFIw0Aof7wfb9/fyjYe7OHy8f7l9eNj8m13/2e+8BwEIDyw3v/kIANTht9/rm2/z4XbibyQ90/mjQ1R/tpl7YmL1jRafAKl0HiQADh7TEAgI39mV/4wHD2ABIT32ACmEEJ705DtfeotPW228fee2d9pqY7Vew7BvrdV6LbzW8eg4+kzaOKqk9wUIEoy79dsAwD9tPZMAY7Veg4SHn7R+gdV6DR4kBBinrbZmgAXEJTUk4SnFYEghEe4fQcp+8IMfinQAM0iDsflwu+86Hksap73/1w+3w5PuQQKs8P3v/AM2H+4AAL77+D184+EjSDAUvPDESwCKPQgZcwD2yAPIpwWSSYCkJzwWUniKPciZuEAaaO/U7+C09V9Yrdfw41Ybd+u38X6rHR6At+u31futNu7W7+C09QEECay+VcOPWj8HoPBO/S38uNUmDk7P21+6zaettnynXqMftdoEEkpI3xUBDByA+PqGrTcO7iQOOGBpIvYXdcDIOHxPQOB7j/9x2PsMDv772xZCCCEIAv5h6JMKIPvu4/cAKBx+Zx8eVOQe4EGFjusFfwoeIC/H4Z+EgoQE/P/S8+ApePA8lQSfgICgy/9RV+xrb0EG/Hs0Mn9hHoIWqJ0gLn8nkT0FOQnuKQC4W6+F7uwpPxKO/feCu56/a4kwD6t3bqu336p5b9+57ekWHIXJ36v/N2qswRv1PJiJk9onMKQFj+mAo2LjOKDSlfPI+97jb0EJiM2H2+H469/cDuME1fd8fKwLE+mopVB6KyXx/gfP8JX656EAT3kkfvLBM09CCYLy7t65I97/4IOQV+WRWP1yDT/592dQQg7E796p4ac//wWv1mv40X/852V7THG2cRww6T1jBwRIACxYEMh3fUGBHeixHqXFD//pH8L49x/vQ7BgQYLBAoeP90PYkkBUUVuDCseH3973Dh9/KzWeNu6z1kzKsF+wYOFnalQ+BODvX/j7Hy3lKU960oOnPH8sPYnVO18Ix8qPecoDVutf8OAp74/rn/eUB5y2PvDu3ql5d+/UgueBt794WybBl3QYVut3BASJ0w+eia98uYbV+h3BgkEC4itfruG09Uzogkb3y+DEfIX75+T9GzlgESJgqKONOxZQAASDAc9vRuWxwdQc+O0rOE7G4zAdJdt78+g4GUBBggJ/L1HTmo4EQB7rCgoJ5Q3kY9zxlRIJBvmgCkBBAhKkAEARQyiPFDMBgFQkhfJIMtHL55ViKZRHgPAbEQHQNjwOgHOYAAFROgN45fefDOAUT4B1wJLmYErrL6cDviSbwQAACTmRiWh+cCXrr3c/UQb8nev9AwQFBQq+y+eAAuzsvF75bP/2KfI35rqjr2oQoteZpIK/WZU/5/37QGTev979bDKQ8/79nSfv/1fdX5fQAaPnfwIPGATdz2A5PaB4B9T/y6j0Fvxqt0CrKQLoJEYygtc8OrZZtIJJB00GcAy1Wy1Ua42B+532Fqq1Rvht4/MZd5yWET9+q7WympEIzk13UgttHh2j3TI7AVZXW7V6feIW3Dw6Nm/BcXtOs2wbn9O4IUG2BVvZFmxlW7BxC06y7ug9G5/PuKmMARylvWX/J3oHDbSCa63oPRsvZ7xa9hbsuvXE0wIAzYMGjp+e2j41BS2urPWNL85OxoqnaXt5DXvnbmJ9S9GC02y4Whs8UVbJch8+SW5Pj9+dCD59T0M2Kj6JwnZsWGI2TV611rhcjNXMnS8eGxUfpV7Fd7+iZAxg3A2LXKzV9LXUdQo1mFx7pF6ohXA+VURdc3XA+GJ7FddWbY5UrTVyd8NcHTC+2NZyYdNbBbo4O8HiylpqDB/XYlTcyA3rrdkCaNttDi7w+N3cIYzCNSo+TL2Ki05zsMahExoSZAygXkgcxE57C72DBnA+nSK6L573b2zhliU7By11HVRrjcT6ltoBx23BowAaFndfPAcWNgaef1UgTGqxiytrQ1twNG5iPKV1wLHdy62mAuS+eI6lNzcT40nw4eXZXdh4JSBMgitLLCuEaS04LxkDmMUN50UrT92XXQln93JN25VswaUEMA83tCqviqgrF7nYXsV3jHnR2T3nlXK/JIPRJlNKB4wvtrWcbXpn4RbcF88H7mWJh7GFjf5JXzT75phXXZydYHFlLTWGj2sxKm7khvXWbAHMy5ZHwTIsPgrgVxHCKFyj4sPUq7joNAdrHDqhIUHGLTjNlqfdgp2FW30fq3y01HVS65uH+RTmgOO04JfPv8oOZqqkFru4sja0BUfjkxpPqR1wHLkvnsM52Oz7xIG0yg5fNDYqnqkF5+B0hTlgFjccKgEwCTCJ/pORcC8uyR7gWQin0YKLgtDhjB7IxJBKgonopXVKpRQzJdryWIv1AKk8SNVPUtK9pHetDFsgA1ICBEGAAqCgoBQAEDHBvxnWlYkoQGag/hMBKGW2B6XyH5TKX9xLKKUMLxPdsHfQAM5tkTMBQEQqktt0I0g3gEmk66/gDfy2Uv0FDgxGaYORUgEZDSx1P0UltlprYKmbrcM7C7fgPjjs+zgLt6YGgH/aQQQmCgqspc874/K2hiBXADLAp8HTJiClwsXZSeqzF2cnI+OTqtPeyqUtGwNouhANgLNwq+8zuNCiAYBSkCoOgtLOf9mJwi4wrANMU0kgRe+Nig9Tr+Im1rdaa2hHNGvBGoBogVOLFRSBQSThtwC9iPgis7ZgDUDW3y4jAADg/mYZ+PQKHJzC/c0ynE+P2PgUIMxqAMNqsNR1UK01EuvLTMAXW2YA6h+PFjgDDCEAae5XrTXQWs7Wgl8+7754PtCW84wXLR+4c7hYhfPp07EA+L//9dcu+rt/bA8KXqxEzJTpEC6urCXeuzg7yWwASfX1F2mYN9PEpzngWO7x4jlwMgiULsDL+NKbm0PjzkF6PKsDCCJ4/R14xLuXALi/WQ7unsFFdgeMAhD/7VFrmRS+OIQjW3Bz8tqOzGGek3XaW2ODyBOsgIlJA2CqYQCMfjeA7yh6pDsxIK+2dAsuDMB+AGI9IIMDxN1w3MVO0gKk8iufxQGmrvP2lQKsr/5ElPpJMJg8DMDpB2A8CxgGQKe9hd5BA8jWieZHS9uFdgBBDE/5RWMm40PYV3+VUH+lQiy0uWgIpVTGPdQpqg7VWgOt5WzTOwu34L54PnAvr/goACZx4QEATs+B1UjbPc128sb9bQ1f1g5wcXaCxZW11NikCp2w3potgFFLnkiCwIpw/fc+Eytu/9FKiktSgOcXIStwpgAkdQBnHXCP+qFz1scowoRrz6okCLPC16u46DQHa6zd0JQgYwDjtjx2C/YUJMzaSBk0DnBXSUtdB9VaI7G+pXbAcVrwqy73xfNCnTGpBS+urBm14LwcsL/PTbiQcDFWpVMSfFlifS04xWTykDGAcTcscrFWs2vBRSnXHqkXaiGcTxVR11wdML7YXsW1VZsjVWuN3N0wVweML7a1XNj0Vhl1cXaCxZW11JixG9ZbswXQttscXGDh1tQhzApfr+Ki0xysceiEhgQZA6gXEgex095C76ABnFvAyqDemTtR4Ze6Dqq1RmJ9S+2A47Rg98Xzoc7wqsdN5WI18Z6DU2PjMSWI83DAcDFWpVMSfFlifS04xWTykDGAcTcscrFW05duwUXJuAUn2bKFcD5VRF1zdcD4YnsV11ZtjlStNXJ3w8IArNYaWOrmarAFiQhgAgSBQPM2dvB+atyh04nn77T/njrPtozXx6YTdNp/S5323xklzFn4DDkLf0DO794iZ+H3w/F04oCzcCvxozXruKkcnGa6l6RexU1svXm5IcG56W6s35/o5ebRMVy3HrZcvSC94OZBA8dPs210xi4IQNkem5CN7eU17J37EMbri49PT61ehwk/xj0y6XToE9JazqcFF4/H1YKv6HxkmTt0P8MSs+liq7UGbudgxfODhw/IvOQjrQXnlQ9jAKMJ6bS3jBdrASlXPpa6zqXbFZCPfHpkzJbzODGzbjG25Q6qCHOZyAGzOEinvYVexbUtd44OTLXWyOSG4+RjIgfMkpBqrYHWcq4Gax21RPkI3bDeMsqHMSF52LIFpLz56FVcdJqDNQ6d0JCgTK8PS4heSBzETnsLvYMGcG6YkP21VwKQxWPg4uykdAdmqeugWmsk1lc7oEk+2PTEdNpbiS5YrTWw1J1NC6aC5y8CkIv7wOJKMYetiHxUa43QfEzykQnArAspMiH3u27meFJCxnl/mnH3wWGYj6IgNAGkV3ETDSYvJQI46YlJc8M8EnJc6XfTeEGLjFOB8zsHm335iELoYrU0LbgoR03skZOeGL3QIk9MUkEpYc3xgo8Celg8KR95zp/ojFiFg9OJW66J6w0zmKk4YF6L7VX8U57XiUlrYzrZZW2z8Xg0H+6Dw75nFo+Bi7OTieEzbbmjDCbuhrk4YBEnplproLXsn/K85i7adXQ8LR95zR+d2znYHICvbEoykNAN6y1zAE0AmUa7nVaLKdpBhskEviLz0au4+EVzsMahEw4/c9kANHW6OIikW/BBAzgvGJDt8jnGJIBclPTALHUdVGuNAaMxccBoPowBTHJAFWvB8wDIVXPUovNh4oDRuTkPBwwXU2BC7nddC0gkH0Uqmo9exU00mbxkDGA0IZ32ViGLVQCOK/1HrUggrxIgRUu34KLykUuP1AnRCy3yxGjFgbQtt9iWa1LXYXPn4oBpi+1VJnOptBOTl+vZljtZPqq1hrEb5uKAWU5MtdZAa3kyl0qb28T1yuAg83RgQjest4zyMVFFo5NPo91aQGaXj17FRac5WOPQCRMIGicfxpaiFxIHsdPeQu+gAZwbJmT7xAIywwOz1HVQrTUS65vmgOOIsyZkmBUnuWC11sBSNxvfVxGQIpV3PhZX1rC4stY3zsN4tPmY5CMTgMMSEl2IBaSc+p8zv4vEQczcghMMJq98ZAIwq9LccBggghkMQYL7lhI+QmAwCMQMCAEGQEQgFv49MASL4B773wCYGcwCAPl/zMGkBIAgBAHETABIMCAIDAEhCET+vBACxAAJAWYGICAE/HtMgCCQ8H8LEBBM4bcQABEgBEOI2QKoAbkIQNTf47Tg4szCuelurN+f6OXm0TFctx7Cpxeqr/eWHeyfZ9+sVTGKu944AG4vr2HvfNAFda0dpwUTfnJ1wLgb9iqurX5JdHF2EoI3bhuOQpe3GzpFbbhaa6C1XNj0VmPCN4n7jTKYTy7qrdkCGLdmq/lSr+Ki0xysceiEhgQZt+A0W867BS+urPV9rKajpa6TWt88zKcwB8yzBS+urOG1/af997bv5dZOrCYznlI7YJ7O99r+U3z04VO8++ERAOCjD5/itf2n1gmn1YJzcLrCACzClpO0d/IET95c/wTCvZMnlowZt+BSAlikGz5t+A745M11OGurlowZqAiDyRXA+GJ7FTe3+TR8+ttq+irCYJwiF9taNp/+4uwEi9v38GT/KQCE8P12+x4uzk4sFTN0w08u6q3ZApi3JQ+DMH7Pqnj1Ki46zcEah05oSJBxC06z5bxb8Cgtrqz1fa5avKxa6jqp9c3DfApzwLxasC7ea0ELDu9FWvBVj19Fld4B83Q2Xbx3PzwKv1/bfxq6yVWOX4kWnIPTFQZgEbacpHc/PMKTN9fD73mLX7UWXEoAi3TDaPG0k8xT/CqoCIPJFcD4YnsV1zrgFXfAog3GKXKxrWXz6S/OTrC4fQ9P9p+GTvJy4b/dvoeLsxMAuPLxq+qGn1zUW0bzEJyb7sb6/Ylebh4do926XIA+HZ321ifXe8sO9s/zSfLiytoAmPMUL6vu31vFxgMftnh9AcBxWjDhx9iioosaaMEHDeA8n0SMKthVj5sl540I6b/MdeqlroNqrZFY3zwc0BjA+MLybsFWWdrDL30Io98FSxuPKUGcx0LCxViVB8ac1Ku4qSaTh3K1qCIXapUuF6vAYs7FHNGCSwmgdkIL4pThe9EEFjbgYhUOTuEu3gKC67IbjHELHrbYXsW1hExDCxuBm5xeAqnhzNlgtMmU0gHji20tFza9VVjAALoEIItU6Ib11mwBtO22HBAmAZlHC+5VXHSagzUOndCQIOMWnGbLtgXPFsg84PvYS7HUdVLrm4f5FOaAtgXPt0rvgFbzoV7FzcXpCgOwCFu2Ko/SWnBeyrVH6oVaCOdTRdQ1VweML7ZXcW3V5kjVWiN3N8zVAeOLbS0XNr1VWdyw3potgLbdzrd6FRed5mCNQyc0JCgXi0qz5b1zF717q1jq9v9Mr+KG96LXNl6+eP3Bw9zb7lRasNbGg62BDXSal/ei1zZewnjBfBCcm+7G+v2JXm4eHaPdatk+9QqrVq/DhB9jB4yenk578DT1nSwbn7+4IUFsz7DVLGVbsNXVb8Fp1q3v2/j8xk1lW7DV1W7BVlYza8GT/rCVlW3BVhZAKysLoJUF0MoCaGVlAbSyAFpZWQCtLIBWVlORY/Jyt9u1GbRCpVKxDmhlW7CVlQXQygJoZWUBtLIAWllZAK0sgFZWFkArC6CVlQXQygJoZWUBtLIAWllZAK0sgFYWQCsrC6CVBdDKygJoZQG0srIAWlkArayKlZPXRA8ePAivDw4OBsbRZ9LGw+Yb9ptJv5fXOPrbw37PqgQOGC2Evo7CdnBwMDDOOl8SfNH5kp4ftp6scQ1a2u9Z+EoEYNQVJnlXfyadL/78KMizHIKi9mtVkANOWlD97jBHG8eBk1pl0vMmkFv3KxmASYXS37rYcYcb5VCj4MnLheLrTXPUJNe2mlwE56a7sX5/ope73a7NoBUqlcpE7zWPjotzQCurmbZgK6sscmZhvVZWzaNjbKyvO9YBrWYGn23BVjOFzwJoNVP4LIBWM4XPAmg1U/gsgFYzhQ8AeGN93WkeHdtMWU0dvtABLYRWs4APAMIHfAiPXJu6V0wMQH5MAggQgJBMnvKU6bRZ4Hup/wfR7NNKMSmnvQAAABB0RVh0TG9kZVBORwAyMDExMDIyMeNZtsEAAAAASUVORK5CYII="

# 화면 설정 (convert를 위해 필수)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Quantum Slither: Black Background Removed")

def get_base_sprites(b64_data):
    """
    [교수님 지적 해결 핵심 함수]
    시트의 검은색 배경(0,0,0)을 알파(투명)로 변환하여 로드
    """
    # 기본 이미지 (데이터 없을 때) - 알파 채널 지원하도록 생성
    def_head = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    def_head.fill((0, 200, 0, 255)) # 투명하지 않은 초록
    def_body = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    def_body.fill((0, 150, 0, 255))
    
    if not b64_data or len(b64_data) < 10:
        return def_head, def_body
    
    try:
        # 1. Base64 디코딩
        sheet_bytes = base64.b64decode(b64_data)
        # 2. 이미지 로드 후 convert() 사용 (convert_alpha() 아님)
        sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert()
        
        # 3. [핵심] 시트 전체에서 순수 검은색(0,0,0)을 투명하게 설정
        # colorkey 방식이 가장 확실하게 특정 색을 날려버립니다.
        sheet.set_colorkey((0, 0, 0))
        
        # 주신 규격: 가로 13px, 세로 14px, 가로 12칸
        fw, fh = 13, 14
        cols = 12
        
        def extract_and_clean(index):
            row, col = divmod(index, cols)
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            # subsurface 시 colorkey(투명도)가 상속됩니다.
            raw_img = sheet.subsurface(rect)
            # 깔끔하게 알파 정보까지 포함된 표면으로 다시 변환
            clean_img = raw_img.convert_alpha() 
            # 게임 크기(20x20)로 확대
            return pygame.transform.scale(clean_img, (CELL, CELL))

        # 머리(79번), 몸통(78번) 추출
        return extract_and_clean(79), extract_and_clean(78)
        
    except Exception as e:
        print(f"이미지 투명화 로드 에러: {e}")
        # 에러 시 기본 분홍색/보라색
        e_head = pygame.Surface((CELL, CELL), pygame.SRCALPHA); e_head.fill((255, 0, 255, 255))
        e_body = pygame.Surface((CELL, CELL), pygame.SRCALPHA); e_body.fill((200, 0, 200, 255))
        return e_head, e_body

# 배경이 날아간 원본 이미지 로드
ORIGINAL_HEAD, ORIGINAL_BODY = get_base_sprites(SHEET_B64)

# 방향별 회전 이미지 테이블 (Alpha가 유지된 상태로 회전)
head_angles = {}
body_angles = {}

def pre_rotate_sprites():
    # 0도(오른쪽), 180도(왼쪽), 90도(위), 270도(아래)
    angles = {(CELL, 0): 0, (-CELL, 0): 180, (0, -CELL): 90, (0, CELL): 270}
    for dir_tuple, angle in angles.items():
        # 회전 시에도 배경 투명도가 유지되도록 처리
        head_angles[dir_tuple] = pygame.transform.rotate(ORIGINAL_HEAD, angle)
        body_angles[dir_tuple] = pygame.transform.rotate(ORIGINAL_BODY, angle)

pre_rotate_sprites()

# 색상 및 환경 설정
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (30, 30, 30)
RED, GOLD, PURPLE, YELLOW = (255, 50, 50), (255, 215, 0), (200, 50, 255), (255, 255, 0)
WALL_COLOR, WALL_BORDER = (120, 100, 100), (80, 60, 60)
GHOST_OVERLAY = (150, 200, 255, 120) # 유령 모드 시 덮어씌울 색상

clock = pygame.time.Clock()
font_main = pygame.font.SysFont("arial", 25, bold=True)

# --- 2. 유틸리티 함수 (좌표 계산 원본 유지) ---
def get_hardcore_pos(snake_coords, exclude_list, head_coords, direction, score):
    hx, hy = head_coords
    dx, dy = direction
    spawn_range = max(10, 40 - (score // 50)) 
    for _ in range(100):
        if random.random() < 0.7:
            rx = random.randint(0, spawn_range) * dx + random.randint(-15, 15) * CELL
            ry = random.randint(0, spawn_range) * dy + random.randint(-15, 15) * CELL
            pos = ((hx + rx) // CELL * CELL, (hy + ry) // CELL * CELL)
        else:
            pos = (((hx + random.randint(-spawn_range, spawn_range) * CELL) // CELL) * CELL,
                   ((hy + random.randint(-spawn_range, spawn_range) * CELL) // CELL) * CELL)
        if pos not in snake_coords and pos not in exclude_list:
            if abs(pos[0] - hx) > CELL*3 or abs(pos[1] - hy) > CELL*3:
                return pos
    return None

def spawn_hardcore_walls(snake_coords, walls, items_pos, head_coords, direction, score):
    start_pos = get_hardcore_pos(snake_coords, walls + items_pos, head_coords, direction, score)
    if not start_pos: return []
    cluster = [start_pos]
    size = random.randint(3, 8); directions = [(0, CELL), (0, -CELL), (CELL, 0), (-CELL, 0)]
    curr = start_pos
    for _ in range(size - 1):
        d = random.choice(directions); nxt = (curr[0] + d[0], curr[1] + d[1])
        if nxt not in snake_coords and nxt not in walls: cluster.append(nxt); curr = nxt
    return cluster

def show_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((30, 0, 0, 200)) # 게임오버 시 반투명 붉은 배경
    screen.blit(overlay, (0, 0))
    t_font = pygame.font.SysFont("arial", 70, bold=True)
    m_font = pygame.font.SysFont("arial", 30, bold=True)
    screen.blit(t_font.render("GAME OVER", True, RED), (WIDTH//2-180, HEIGHT//2-100))
    screen.blit(m_font.render(f"Final Score: {score}", True, WHITE), (WIDTH//2-80, HEIGHT//2))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    # 스네이크 상태 (x, y, sdx, sdy)
    snake = [(0, 0, CELL, 0), (-CELL, 0, CELL, 0), (-CELL*2, 0, CELL, 0)]
    direction, next_dir = (CELL, 0), (CELL, 0)
    items, walls = [], []; score, move_acc = 0, 0.0
    base_delay, ghost_timer, thunder_timer = 90, 0, 0

    while True:
        dt = clock.tick(TARGET_FPS)
        now = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and direction != (0, CELL): next_dir = (0, -CELL)
                elif e.key == pygame.K_DOWN and direction != (0, -CELL): next_dir = (0, CELL)
                elif e.key == pygame.K_LEFT and direction != (CELL, 0): next_dir = (-CELL, 0)
                elif e.key == pygame.K_RIGHT and direction != (-CELL, 0): next_dir = (CELL, 0)

        is_ghost, is_thunder = now < ghost_timer, now < thunder_timer
        delay = base_delay * 0.6 if is_thunder else base_delay
        move_acc += dt
        
        if move_acc >= delay:
            move_acc -= delay
            direction = next_dir
            hx, hy, _, _ = snake[0]
            new_hx, new_hy = hx + direction[0], hy + direction[1]
            head_coords = (new_hx, new_hy)
            s_coords = [(s[0], s[1]) for s in snake]
            
            if not is_ghost and (head_coords in walls or head_coords in s_coords): return score
            
            snake.insert(0, (new_hx, new_hy, direction[0], direction[1]))
            ate = False
            for it in items[:]:
                if head_coords == it['pos']:
                    ate = True
                    score += (20 if is_thunder else 10)
                    if it['type'] == 'NANO': snake = snake[:max(3, len(snake)//2)]
                    elif it['type'] == 'GHOST': ghost_timer = now + 5000
                    elif it['type'] == 'THUNDER': thunder_timer = now + 5000
                    items.remove(it)
            if not ate: snake.pop()
            
            # 자원 관리 및 생성
            h_c = (snake[0][0], snake[0][1])
            items = [i for i in items if abs(i['pos'][0]-h_c[0]) < 1200 and abs(i['pos'][1]-h_c[1]) < 1200]
            walls = [w for w in walls if abs(w[0]-h_c[0]) < 1500 and abs(w[1]-h_c[1]) < 1500]
            
            while len(items) < 8:
                s_c_now = [(s[0], s[1]) for s in snake]
                p = get_hardcore_pos(s_c_now, [i['pos'] for i in items] + walls, h_c, direction, score)
                if not p: break
                rand = random.random()
                if rand < 0.8: t, c = "NORMAL", RED
                elif rand < 0.885: t, c = "GHOST", PURPLE
                elif rand < 0.97: t, c = "THUNDER", YELLOW
                else: t, c = "NANO", GOLD
                items.append({'pos': p, 'type': t, 'color': c})
            
            target_w = min(600, 40 + (score // 2)) 
            if len(walls) < target_w:
                for _ in range(3):
                    s_c_now = [(s[0], s[1]) for s in snake]
                    new_block = spawn_hardcore_walls(s_c_now, walls, [i['pos'] for i in items], h_c, direction, score)
                    walls.extend(new_block)

        # --- 렌더링 ---
        cam_x, cam_y = WIDTH//2 - snake[0][0], HEIGHT//2 - snake[0][1]
        screen.fill(GRAY)
        
        # 격자
        gx, gy = ((snake[0][0]-WIDTH//2)//CELL)*CELL, ((snake[0][1]-HEIGHT//2)//CELL)*CELL
        for x in range(gx, gx+WIDTH+CELL*2, CELL): pygame.draw.line(screen, (35, 35, 35), (x+cam_x, 0), (x+cam_x, HEIGHT))
        for y in range(gy, gy+HEIGHT+CELL*2, CELL): pygame.draw.line(screen, (35, 35, 35), (0,y+cam_y), (WIDTH, y+cam_y))
        
        # 벽 및 아이템
        for w in walls:
            dx, dy = w[0]+cam_x, w[1]+cam_y
            if -20 < dx < WIDTH+20 and -20 < dy < HEIGHT+20:
                pygame.draw.rect(screen, WALL_COLOR, (dx, dy, CELL, CELL))
        for it in items:
            dx, dy = it['pos'][0]+cam_x, it['pos'][1]+cam_y
            if -20 < dx < WIDTH+20 and -20 < dy < HEIGHT+20:
                pygame.draw.rect(screen, it['color'], (dx, dy, CELL, CELL))

        # 뱀 그리기 (Alpha 채널 적용 완료)
        for i, (sx, sy, sdx, sdy) in enumerate(snake):
            dp = (sx+cam_x, sy+cam_y)
            if -20 < dp[0] < WIDTH+20 and -20 < dp[1] < HEIGHT+20:
                s_dir = (sdx, sdy)
                # 방향에 맞는 이미지를 테이블에서 가져옴
                img = head_angles.get(s_dir, ORIGINAL_HEAD) if i == 0 else body_angles.get(s_dir, ORIGINAL_BODY)
                
                screen.blit(img, dp)
                
                # 유령 상태일 때 덮어씌울 알파 레이어
                if is_ghost:
                    ghost_surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                    ghost_surf.fill(GHOST_OVERLAY)
                    screen.blit(ghost_surf, dp)
        
        screen.blit(font_main.render(f"SCORE: {score}", True, WHITE), (20, 20))
        pygame.display.flip()

if __name__ == "__main__":
    while True:
        final_score = main()
        if not show_game_over(final_score): break