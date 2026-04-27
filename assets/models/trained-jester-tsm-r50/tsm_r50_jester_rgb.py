_base_ = [
    '../../../third_party/mmaction2/configs/_base_/models/tsm_r50.py',
    '../../../third_party/mmaction2/configs/_base_/default_runtime.py',
    '../../../third_party/mmaction2/configs/_base_/schedules/sgd_tsm_50e.py',
]

default_scope = 'mmaction'

dataset_type = 'RawframeDataset'
num_classes = 27

data_root = 'data/external/jester/raw/20bn-jester-v1'
data_root_val = data_root
ann_file_train = 'data/processed/jester/mmaction2/jester_train_list_rawframes.txt'
ann_file_val = 'data/processed/jester/mmaction2/jester_val_list_rawframes.txt'
ann_file_test = ann_file_val

file_client_args = dict(io_backend='disk')

model = dict(cls_head=dict(num_classes=num_classes, dropout_ratio=0.5))

train_pipeline = [
    dict(type='SampleFrames', clip_len=1, frame_interval=1, num_clips=8),
    dict(type='RawFrameDecode', **file_client_args),
    dict(type='Resize', scale=(-1, 256)),
    dict(
        type='MultiScaleCrop',
        input_size=224,
        scales=(1, 0.875, 0.75, 0.66),
        random_crop=False,
        max_wh_scale_gap=1,
        num_fixed_crops=13,
    ),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    # Jester contains left/right directional labels, so we disable naive flips.
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='PackActionInputs'),
]

val_pipeline = [
    dict(
        type='SampleFrames',
        clip_len=1,
        frame_interval=1,
        num_clips=8,
        test_mode=True,
    ),
    dict(type='RawFrameDecode', **file_client_args),
    dict(type='Resize', scale=(-1, 256)),
    dict(type='CenterCrop', crop_size=224),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='PackActionInputs'),
]

test_pipeline = [
    dict(
        type='SampleFrames',
        clip_len=1,
        frame_interval=1,
        num_clips=8,
        test_mode=True,
        twice_sample=True,
    ),
    dict(type='RawFrameDecode', **file_client_args),
    dict(type='Resize', scale=(-1, 256)),
    dict(type='ThreeCrop', crop_size=256),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='PackActionInputs'),
]

train_dataloader = dict(
    batch_size=8,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_train,
        data_prefix=dict(img=data_root),
        filename_tmpl='{:05}.jpg',
        pipeline=train_pipeline,
    ),
)

val_dataloader = dict(
    batch_size=8,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_val,
        data_prefix=dict(img=data_root_val),
        filename_tmpl='{:05}.jpg',
        pipeline=val_pipeline,
        test_mode=True,
    ),
)

test_dataloader = dict(
    batch_size=1,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_test,
        data_prefix=dict(img=data_root_val),
        filename_tmpl='{:05}.jpg',
        pipeline=test_pipeline,
        test_mode=True,
    ),
)

val_evaluator = [dict(type='AccMetric'), dict(type='ConfusionMatrix')]
test_evaluator = val_evaluator

default_hooks = dict(
    checkpoint=dict(type='CheckpointHook', interval=1, max_keep_ckpts=3, save_best='auto'),
    logger=dict(type='LoggerHook', interval=20),
)

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=20, val_begin=1, val_interval=1)
param_scheduler = [
    dict(type='LinearLR', start_factor=0.1, by_epoch=True, begin=0, end=2),
    dict(type='CosineAnnealingLR', T_max=18, by_epoch=True, begin=2, end=20),
]

optim_wrapper = dict(
    constructor='TSMOptimWrapperConstructor',
    paramwise_cfg=dict(fc_lr5=True),
    optimizer=dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0005),
    clip_grad=dict(max_norm=20, norm_type=2),
)

randomness = dict(seed=42, deterministic=False)
work_dir = './work_dirs/jester_tsm_r50'
