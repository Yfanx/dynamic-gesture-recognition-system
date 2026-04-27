_base_ = [
    './tsm_r50_jester_rgb.py',
]

default_scope = 'mmaction'

num_classes = 27

data_root = 'data/external/jester/raw/20bn-jester-v1'
data_root_val = data_root
ann_file_train = 'data/processed/jester/mmaction2_full/jester_train_list_rawframes.txt'
ann_file_val = 'data/processed/jester/mmaction2_full/jester_val_list_rawframes.txt'
ann_file_test = ann_file_val

load_from = 'assets/models/tsm_r50_1x1x8_50e_jester_rgb-c799267e.pth'

model = dict(
    cls_head=dict(num_classes=num_classes, dropout_ratio=0.5),
)

train_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        ann_file=ann_file_train,
        data_prefix=dict(img=data_root),
    ),
)

val_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        ann_file=ann_file_val,
        data_prefix=dict(img=data_root_val),
        test_mode=True,
    ),
)

test_dataloader = dict(
    batch_size=1,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        ann_file=ann_file_test,
        data_prefix=dict(img=data_root_val),
        test_mode=True,
    ),
)

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=12, val_begin=1, val_interval=1)
param_scheduler = [
    dict(type='LinearLR', start_factor=0.1, by_epoch=True, begin=0, end=1),
    dict(type='CosineAnnealingLR', T_max=11, by_epoch=True, begin=1, end=12),
]

optim_wrapper = dict(
    constructor='TSMOptimWrapperConstructor',
    paramwise_cfg=dict(fc_lr5=True),
    optimizer=dict(type='SGD', lr=0.001, momentum=0.9, weight_decay=0.0005),
    clip_grad=dict(max_norm=20, norm_type=2),
)

default_hooks = dict(
    checkpoint=dict(
        type='CheckpointHook',
        interval=1,
        max_keep_ckpts=5,
        save_best='acc/top1',
        rule='greater',
    ),
    logger=dict(type='LoggerHook', interval=20),
)

randomness = dict(seed=42, deterministic=False)
work_dir = 'work_dirs/jester_tsm_r50_finetune_v1'

train_dataloader['dataset']['ann_file'] = ann_file_train
train_dataloader['dataset']['data_prefix'] = dict(img=data_root)
val_dataloader['dataset']['ann_file'] = ann_file_val
val_dataloader['dataset']['data_prefix'] = dict(img=data_root_val)
test_dataloader['dataset']['ann_file'] = ann_file_test
test_dataloader['dataset']['data_prefix'] = dict(img=data_root_val)
