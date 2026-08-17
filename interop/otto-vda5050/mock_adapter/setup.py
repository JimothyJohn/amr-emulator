from setuptools import setup

package_name = "vda5050_mock_adapter"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    description="Instantly-succeeding VDA5050 connector adapter for interop tests",
    license="MIT",
    entry_points={
        "console_scripts": [
            "mock_adapter = vda5050_mock_adapter.mock_adapter:main",
        ],
    },
)
