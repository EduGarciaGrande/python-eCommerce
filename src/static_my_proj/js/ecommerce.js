$(document).ready(function () {
                // Contact form handler
                var contactForm = $(".contact-form"), contactFormMethod = contactForm.attr("method"),
                    contactFormEndpoint = contactForm.attr("action");

                function displaySubmitting(submitBtn, defaultText, doSubmit){
                    if (doSubmit){
                        submitBtn.addClass("disabled");
                        submitBtn.html('<i class="fa fa-spin fa-spinner"></i>Sending...');
                    }
                    else{
                        submitBtn.removeClass("disabled");
                        submitBtn.html(defaultText);
                    }
                }

                contactForm.submit(function (event) {
                    event.preventDefault();
                    var contactFormData = contactForm.serialize(), thisForm = $(this),
                        contactFormSubmitBtn = contactForm.find("[type='submit']"),
                        contactFormSubmitBtnTxt = contactFormSubmitBtn.text();
                    displaySubmitting(contactFormSubmitBtn, "", true);

                    $.ajax({
                        method: contactFormMethod,
                        url: contactFormEndpoint,
                        data: contactFormData,
                        success: function(data){
                            thisForm[0].reset();
                            $.alert({
                                title: "Success!",
                                content: data.message,
                                theme: "modern"
                            });

                            setTimeout(function () {
                                displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
                            }, 500);
                        },
                        error:function (error) {
                            console.log(error.responseJSON);
                            var jsonData = error.responseJSON, msg = "";

                            $.each(jsonData, function (key, value) {
                                msg += key + ": " + value[0].message + "<br/>";
                            });

                            $.alert({
                                title: "Oops!",
                                content: msg,
                                theme: "modern"
                            });

                             setTimeout(function () {
                                displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
                            }, 500);
                        }
                    });
                });


                // Auto Search
                var searchForm = $(".search-form"), searchInput = searchForm.find("[name='q']");
                var searchBtn = searchForm.find("[type='submit']"), typingTimer, typingInterval = 500;

                searchInput.keyup(function (event) {
                    clearTimeout(typingTimer);
                    typingTimer = setTimeout(performSearch, typingInterval);
                });

                searchInput.keydown(function (event) {
                    clearTimeout(typingTimer);
                });

                function displaySearching(){
                    searchBtn.addClass("disabled");
                    searchBtn.html('<i class="fa fa-spin fa-spinner"></i>Searching...');
                }

                function performSearch() {
                    displaySearching();
                    var query = searchInput.val();
                    setTimeout(function () {
                        window.location.href = '/search/?q=' + query;
                    }, 1000);
                }


                // Cart + Add products
                var productForm = $(".form-product-ajax");

                function getOwnedProduct(productId, submitSpan){
                    var actionEndpoint = '/orders/endpoint/verify/ownership/';
                    var httpMethod = 'GET';
                    var data = {
                        product_id: productId
                    };

                    var isOwner;
                    $.ajax({
                        url: actionEndpoint,
                        method: httpMethod,
                        data: data,
                        success: function (data) {
                            if (data.owner){
                                isOwner = true;
                                submitSpan.html("<a class='btn btn-warning' href='/library/'>In Library</a>");
                            }
                            else
                                isOwner = false;
                        },
                        error: function () {

                        }
                    });

                    return isOwner;
                }

                $.each(productForm, function (index, object) {
                    var $this = $(this);
                    var isUser = $this.attr("data-user");
                    var submitSpan = $this.find(".submit-span");
                    var productInput = $this.find("[name='product_id']");
                    var productId = productInput.attr("value");
                    var productIsDigital = productInput.attr("data-is-digital");

                    if (productIsDigital && isUser)
                        getOwnedProduct(productId, submitSpan);
                });

                // Submitting form is not allowed
                productForm.submit(function (event) {
                    event.preventDefault();

                    var thisForm = $(this), actionEndpoint = thisForm.attr("action"),
                        httpMethod = thisForm.attr("method"),
                        formData = thisForm.serialize();

                    $.ajax({
                        url: actionEndpoint,
                        method: httpMethod,
                        data: formData,
                        success: function (data) {
                            var submitSpan = thisForm.find(".submit-span"),
                                navbarCount = $(".navbar-cart-count");

                            navbarCount.text(data.cartItemCount);

                            if(data.added){
                                submitSpan.html("<div class=\"btn-group\">" +
                                    "<a class=\"btn btn-link\" href=\"/cart/\">In cart</a>" +
                                    "<button type=\"submit\" class=\"btn btn-link\">Remove ?</button></div>");
                            } else {
                                submitSpan.html("<button type=\"submit\" class=\"btn btn-success\">Add to cart</button>");
                            }

                            var currentPath = window.location.href;
                            if(currentPath.indexOf("cart") != -1){
                                refreshCart();
                            }
                        },
                        error: function (errorData) {
                            $.alert({
                                title: "Ooops!",
                                content: "An error occurred",
                                theme: "modern"
                            });
                        }
                    })
                });

                function refreshCart() {
                    var cartTable = $(".cart-table"), cartBody = cartTable.find(".cart-body"),
                        productRows = cartBody.find(".cart-product"),
                        currentUrl = window.location.href;

                    var refreshCartUrl = '/api/cart/', refreshCartMethod = "GET", data = {};
                    $.ajax({
                        url: refreshCartUrl,
                        method: refreshCartMethod,
                        data: data,
                        success: function(data){
                            var hiddenCartItemRemoveForm = $(".cart-item-remove-form");
                            if (data.products.length > 0){
                                productRows.html(" ");

                                i = data.products.length;
                                $.each(data.products, function (index, value) {
                                    var newCartItemRemove = hiddenCartItemRemoveForm.clone();
                                    newCartItemRemove.css("display", "block");
                                    newCartItemRemove.find(".cart-item-product-id").val(value.id);
                                    cartBody.prepend("<tr><th scope=\"row\">" + i + "</th><td><a href='" + value.url + "'>" +
                                        value.name + "</a>" + newCartItemRemove.html() + "</td><td>" + value.price +  "</td></tr>");
                                    i--;
                                });

                                cartBody.find(".cart-subtotal").text(data.subtotal);
                                cartBody.find(".cart-total").text(data.total);
                            } else{
                                window.location.href = currentUrl;
                            }
                        },
                        error: function(errorData){
                            $.alert({
                                title: "Ooops!",
                                content: "An error occurred",
                                theme: "modern"
                            });
                        }
                    })
                }
            });
