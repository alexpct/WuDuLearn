from flask import jsonify, Blueprint, request

dialog_bp = Blueprint('dialog_bp', __name__)

@dialog_bp.route('/dialog/<modul>/<int:dialog_id>', methods=['GET'])
def get_dialog(modul, dialog_id):
    # Setze locale auf den Wert des Query-Parameters oder default 'de'
    locale = request.args.get('locale', 'de')

    from app import app, mysql

    cursor = mysql.connection.cursor()
    query = """
    SELECT * FROM Dialog
    WHERE ID = %s AND Modul = %s AND Locale = %s
    """
    cursor.execute(query, (dialog_id, modul, locale))
    dialog = cursor.fetchone()
    cursor.close()

    if dialog:
        dialog_data = {
            'Modul': dialog[0],
            'ID': dialog[1],
            'Part': dialog[2],
            'Text': dialog[3],
            'Locale': dialog[4],
            'A1': dialog[5],
            'A1ID': dialog[6],
            'A2': dialog[7],
            'A2ID': dialog[8],
            'A3': dialog[9],
            'A3ID': dialog[10]
        }
        return jsonify(dialog_data)
    else:
        return jsonify({'error': 'Dialog not found'}), 404
