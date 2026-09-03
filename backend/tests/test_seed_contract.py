from app.scripts.seed_demo import CHANNELS, PRODUCTS


def test_seed_matches_mock_fixture_catalog() -> None:
    assert {channel.code for channel in CHANNELS} == {"shopee", "tiktok", "website"}
    assert {product.sku for product in PRODUCTS} == {"TEE-BLK-M", "TEE-WHT-L", "CAP-WHT"}
