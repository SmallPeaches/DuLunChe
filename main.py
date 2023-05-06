import argparse
import yaml
import logging
from dulunche import AutoDuLunChe

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--config',type=str,default='./config.yml')
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s]: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    with open(args.config,'r',encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    dlc = AutoDuLunChe(**config)
    dlc.start()
