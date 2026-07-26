"""
Model registries for the benchmarking wrapper.

Weights are hosted on the Digital Eye for Mammography (DEM) release pages
(Terzi et al., 2025; https://github.com/cbddobvyz/digitaleye-mammography).
DEM is GPL-3.0; it is cloned/downloaded at runtime and is NOT vendored here.
"""

BASE_URL_YOLO = "https://github.com/cbddobvyz/digitaleye-mammography/releases/download/shared-models.v2/"
BASE_URL_MMDET = "https://github.com/cbddobvyz/digitaleye-mammography/releases/download/shared-models.v1/"

# (filename, download_url, sha256)
YOLO_MODELS = [
    ("yolo10_l.pt", BASE_URL_YOLO + "yolo10_l.pt", "a4c7b0a05c63517cc6c49dba0942143c9a29daa118b9f57d875c40c83c3b1782"),
    ("yolo10_m.pt", BASE_URL_YOLO + "yolo10_m.pt", "f07daee9f685a248832df79234d8fc85f67ddb0add13e34bccecc732c2507dcb"),
    ("yolo10_n.pt", BASE_URL_YOLO + "yolo10_n.pt", "87db4f779de067f7b73df853559604c96abe2e905f08d2d984e07b524b7c5a2f"),
    ("yolo10_s.pt", BASE_URL_YOLO + "yolo10_s.pt", "1dd025b8e98af57d742d469115d9f6178d85067c40ed1348f0b5089b4e2a6648"),
    ("yolo10_x.pt", BASE_URL_YOLO + "yolo10_x.pt", "b0a6d94e469ea073935def4ec70b517acdfd3bbc6c5e8b77e8322ef5f622863c"),
    ("yolo11_l.pt", BASE_URL_YOLO + "yolo11_l.pt", "b2a15e0b435ee671de229614fe7fa4d8d9a24c1a4ddfd2c103b591386155193f"),
    ("yolo11_m.pt", BASE_URL_YOLO + "yolo11_m.pt", "f67ef4e01f90c159d995653064e756a466fa6302f727772d3b9774f19824960a"),
    ("yolo11_n.pt", BASE_URL_YOLO + "yolo11_n.pt", "4c6ed69c85775bfe7642a428489fc0a90f53cb3ac7b164eb7da7220ef9549a14"),
    ("yolo11_s.pt", BASE_URL_YOLO + "yolo11_s.pt", "4d4ff958accc0c165a51cd6a5fd39962cefb05dca15c7302e81d790d60cfe758"),
    ("yolo11_x.pt", BASE_URL_YOLO + "yolo11_x.pt", "32c81883d52ab47c15fbd2cfba33c33e3257de955ee72937164a7b7abe136f7e"),
    ("yolo8_l.pt", BASE_URL_YOLO + "yolo8_l.pt", "18e24afb243e20a0dc15be13695f0e16d2934d0fa8231fddd7c73a8de198458f"),
    ("yolo8_m.pt", BASE_URL_YOLO + "yolo8_m.pt", "b35104bb5295831b036295467501de12e96210297d0b24f0f925d5c13b5befc1"),
    ("yolo8_n.pt", BASE_URL_YOLO + "yolo8_n.pt", "8143c7ea8fbd83f9b691d83395b3a04b071325c09d8d6ab2ac9e58a07794c29f"),
    ("yolo8_s.pt", BASE_URL_YOLO + "yolo8_s.pt", "a53501de377e37b878bbd92594b577ebb48e9356007552c61dfa544adfd03b2f"),
    ("yolo8_x.pt", BASE_URL_YOLO + "yolo8_x.pt", "94892c0909981992c7dc3da51af6fc4c9331560bac1cdf36e4f66bf8e98ccc15"),
    ("yolo9_c.pt", BASE_URL_YOLO + "yolo9_c.pt", "7eeb39cf839ac5b4e43527c84079b0497a253e8dc703ef1b0b753544bd2896f4"),
    ("yolo9_e.pt", BASE_URL_YOLO + "yolo9_e.pt", "b612084f868ec90fc873636cc5e2bc4ad02e6130cf85f98972ac1b10d5f37f90"),
    ("yolo9_m.pt", BASE_URL_YOLO + "yolo9_m.pt", "6ed1c0138fb943a8850b8a99cac7c623c4bc8437ea1703bfbefedb3447baf637"),
    ("yolo9_s.pt", BASE_URL_YOLO + "yolo9_s.pt", "5e0502bc0b7585dc27be252a2c494a313d4ae669b8ee77807a8dadf67b368f83"),
    ("yolo9_t.pt", BASE_URL_YOLO + "yolo9_t.pt", "2173225ab045bda406fed431bcc2d9b9fcdab0e2191ac0a88253e5b195a73cf9"),
]

# SHA256 left as PLACEHOLDER (skips verification). Fill in if you want integrity checks.
MMDET_MODELS = [
    ("atss.pth", BASE_URL_MMDET + "atss.pth", "PLACEHOLDER"),
    ("cascade_rcnn.pth", BASE_URL_MMDET + "cascade_rcnn.pth", "PLACEHOLDER"),
    ("deformable_detr.pth", BASE_URL_MMDET + "deformable_detr.pth", "PLACEHOLDER"),
    ("detr.pth", BASE_URL_MMDET + "detr.pth", "PLACEHOLDER"),
    ("doublehead_rcnn.pth", BASE_URL_MMDET + "doublehead_rcnn.pth", "PLACEHOLDER"),
    ("dynamic_rcnn.pth", BASE_URL_MMDET + "dynamic_rcnn.pth", "PLACEHOLDER"),
    ("fasterrcnn.pth", BASE_URL_MMDET + "fasterrcnn.pth", "PLACEHOLDER"),
    ("fcos.pth", BASE_URL_MMDET + "fcos.pth", "PLACEHOLDER"),
    ("retina_net.pth", BASE_URL_MMDET + "retina_net.pth", "PLACEHOLDER"),
    ("varifocal_net.pth", BASE_URL_MMDET + "varifocal_net.pth", "PLACEHOLDER"),
    ("yolo_v3.pth", BASE_URL_MMDET + "yolo_v3.pth", "PLACEHOLDER"),
]

# MMDetection config paths, relative to the cloned DEM repo.
MMDET_CONFIG_MAP = {
    "atss.pth": "configs/atss_config.py",
    "cascade_rcnn.pth": "configs/cascade_rcnn_config.py",
    "deformable_detr.pth": "configs/deformable_detr_config.py",
    "detr.pth": "configs/detr_config.py",
    "doublehead_rcnn.pth": "configs/doublehead_rcnn_config.py",
    "dynamic_rcnn.pth": "configs/dynamic_rcnn_config.py",
    "fasterrcnn.pth": "configs/fasterrcnn_config.py",
    "fcos.pth": "configs/fcos_config.py",
    "retina_net.pth": "configs/retina_net_config.py",
    "varifocal_net.pth": "configs/varifocal_net_config.py",
    "yolo_v3.pth": "configs/yolo_v3_config.py",
}
