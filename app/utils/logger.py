import logging

def setup_logger(nome_modulo):

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s', #  estou falando como ele deve formatar as mensagens de log, nesse caso ele vai mostrar a data e hora, o nível do log e a mensagem em si.
        encoding='utf-8'
        )
    
    return logging.getLogger(nome_modulo)