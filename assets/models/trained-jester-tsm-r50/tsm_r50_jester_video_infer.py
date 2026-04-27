_base_ = ["../../../third_party/mmaction2/configs/_base_/models/tsm_r50.py"]

default_scope = "mmaction"

model = dict(
    cls_head=dict(
        num_classes=27,
        average_clips="prob",
    ),
)

dataset_type = "VideoDataset"
file_client_args = dict(io_backend="disk")

test_pipeline = [
    dict(type="DecordInit", **file_client_args),
    dict(
        type="SampleFrames",
        clip_len=1,
        frame_interval=1,
        num_clips=8,
        test_mode=True,
    ),
    dict(type="DecordDecode"),
    dict(type="Resize", scale=(-1, 256)),
    dict(type="CenterCrop", crop_size=224),
    dict(type="FormatShape", input_format="NCHW"),
    dict(
        type="PackActionInputs",
        meta_keys=("img_shape", "modality", "total_frames", "label"),
    ),
]

test_dataloader = dict(
    batch_size=1,
    num_workers=2,
    persistent_workers=False,
    sampler=dict(type="DefaultSampler", shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=None,
        data_prefix=dict(video=""),
        pipeline=test_pipeline,
        test_mode=True,
    ),
)
