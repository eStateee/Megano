from django.db import models
from django.urls import reverse_lazy
from photologue.models import Photo, Gallery


class Categories(models.Model):
    title = models.CharField(max_length=50, blank=False, verbose_name="Название")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = "Категория товаров"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.title

    @staticmethod
    def get_name_by_slug(slug):
        return Categories.objects.values("title").filter(slug=slug).first()


class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Goods(models.Model):
    part_num = models.IntegerField(null=False, blank=False, verbose_name="Артикул")
    title = models.CharField(max_length=255, null=False, blank=False, verbose_name="Название")
    short_description = models.CharField(max_length=255, null=False, blank=False, verbose_name="Короткое Описание")
    description = models.TextField(null=False, blank=False, verbose_name="Полное описание")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, verbose_name="Цена")
    amount = models.IntegerField(null=False, blank=False, verbose_name="Остаток")
    free_delivery = models.BooleanField(default=False, verbose_name="Бесплатная доставка")
    sort_index = models.IntegerField(default=1, null=False, blank=False, verbose_name="Индекс сортировки")
    limited = models.BooleanField(default=False, null=False, blank=False, verbose_name="Спецпредложение")
    is_published = models.BooleanField(default=True, null=False, blank=False, verbose_name="Опубликовано")
    date_published = models.DateField(auto_now=True, null=False, blank=False, verbose_name="Дата публикации")
    category = models.ForeignKey("Categories", on_delete=models.CASCADE, null=False, blank=False,
                                 related_name="goods", verbose_name="Категория")
    tags = models.ManyToManyField("Tags", blank=True,
                                  related_name="goods_with_tag", verbose_name="Теги")
    photo = models.ForeignKey(
        Photo,
        verbose_name="Главное фото",
        on_delete=models.SET_NULL,
        null=True)
    gallery = models.ForeignKey(
        Gallery,
        verbose_name="Галерея товара",
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("date_published",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy("product", kwargs={"category_slug": self.category.slug, "product_id": self.pk})


class Reviews(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=False, blank=False,
                             related_name="user_reviews", verbose_name="Пользователь")
    good = models.ForeignKey("Goods", on_delete=models.CASCADE, null=False, blank=False,
                             related_name="reviews", verbose_name="Товар")
    text = models.TextField(null=False, blank=False, verbose_name="Текст")
    date_published = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("date_published",)

    def __str__(self):
        return f"{self.date_published} {self.user} {self.good}"
