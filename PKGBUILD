# Maintainer: Ilya Bushmelev top72272bebr@gmail.com
pkgname=python-expa
pkgver=0.1.0
pkgrel=1
pkgdesc="Simple EXpression PArser (eval, but safe)"
arch=('any')
url="https://github.com/ilya-bushmelev/expa.py"
license=('MIT')
depends=('python')
makedepends=('python-build' 'python-installer' 'python-wheel')

# Указываем конкретное имя папки, чтобы не было сюрпризов
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

# В Arch принято явно указывать папку, куда распаковался архив
_folder="expa.py-$pkgver"

build() {
    cd "$srcdir/$_folder"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$_folder"
    python -m installer --destdir="$pkgdir" dist/*.whl
}