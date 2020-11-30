import argparse

import numpy as np

import PIL
import tqdm
import os

import cv2


import sys
sys.path.append('..')

from backend.ml.hnsw_wrapper import Index
from backend.ml.models import BeheadedDenseNet121, calc_embed
from calc_metrics import upload_model

def images2embeds(args):

    model = upload_model(args).train(False)

    embeds = []

    for data in os.walk(args.img_dir):
        path, subdirs, files = data
        relative = os.path.relpath(path, args.img_dir)
        print(path)
        for f in tqdm.tqdm(files, position=0):
            if f.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png']:
                continue
            file_path = os.path.join(path, f)
            relative_file_path = os.path.join(relative, f)
            try:
                e = calc_embed(model, file_path)
                embeds.append([relative_file_path, e])
            except Exception as e:
                print(e)

    np.save(args.out_embeds_path, embeds)


def embeds2index(args):
    assert args.embeds_path[-4:] == '.npy', 'required embeddings must be in npy format'
    embeds = np.load(args.embeds_path, allow_pickle=True)
    dim = len(embeds[0][1])

    index = Index(space='cosine', dim=dim)

    index.init_index(max_elements=len(embeds), ef_construction=100, M=64)
    index.set_ef(64)
    emb_vectors = np.array([e[1] for e in embeds])
    emb_names = np.array([e[0] for e in embeds])
    index.add_items(emb_vectors, ids=emb_names)

    labels, distances = index.knn_query(emb_vectors, k=1)

    recall = np.mean([l[0] == name for l, name in zip(labels, emb_names)])
    print("Recall for built index: {}".format(recall))

    index.save_index(args.out_index_path)



if __name__=='__main__':
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    images2embeds_parser = subs.add_parser('images2embeds')
    embeds2index_parser = subs.add_parser('embeds2index')

    EMBEDDINGS_DESCRIPTION = 'npy format contains list ' + \
        'with pairs (embed_name : str, embed : np.array))'

    # Learning options
    images2embeds_parser.add_argument('--img-dir', type=str, required=True,
                    help='Directory with images for processing.')
    images2embeds_parser.add_argument('--out-embeds-path', type=str, default='embeds.npy',
                    help='Output path for file with embeddings: {}.'.format(EMBEDDINGS_DESCRIPTION))
    images2embeds_parser.add_argument('--model-name', type=str, required=False, default='BeheadedDenseNet121',
                        help='Model name for image processing.')

    embeds2index_parser.add_argument('--embeds-path', type=str, required=True,
                    help='Input file with embeddings: {}.'.format(EMBEDDINGS_DESCRIPTION))
    embeds2index_parser.add_argument('--out-index-path', type=str, default='hnsw.zip',
                    help='Output path for built hnsw index in zip format.')


    images2embeds_parser.set_defaults(func=images2embeds)
    embeds2index_parser.set_defaults(func=embeds2index)


    parsed = parser.parse_args()
    parsed.func(parsed)
